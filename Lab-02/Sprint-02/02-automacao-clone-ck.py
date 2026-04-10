"""
Lab02S02 - Script de Automacao: Clone de Repositorios + Coleta de Metricas CK
(Evolucao do Sprint 1 com suporte a RESUME para processar todos os 1000 repos)

Uso:
    python 02-automacao-clone-ck.py                     # processa todos (com resume automatico)
    python 02-automacao-clone-ck.py --limit 50          # processa apenas 50 repos
    python 02-automacao-clone-ck.py --repo owner/name   # processa um repo especifico
    python 02-automacao-clone-ck.py --reset              # apaga progresso e recomeca

Pre-requisitos:
    - Java 8+ instalado (java no PATH)
    - Git instalado (git no PATH)
    - Arquivo data/repos_java_top1000.csv gerado pelo notebook 01
    - ck-0.7.0-jar-with-dependencies.jar na pasta tools/
      (baixar de: https://repo1.maven.org/maven2/com/github/mauricioaniche/ck/0.7.0/ck-0.7.0-jar-with-dependencies.jar)
"""

import os
import sys
import subprocess
import shutil
import argparse
import json
import time
from pathlib import Path
from datetime import datetime

import pandas as pd

# --- Configuracao ---
BASE_DIR = Path(__file__).resolve().parent
REPOS_CSV = BASE_DIR / "data" / "repos_java_top1000.csv"
TOOLS_DIR = BASE_DIR / "tools"
CK_JAR = TOOLS_DIR / "ck-0.7.0-jar-with-dependencies.jar"
CLONE_DIR = BASE_DIR / "data" / "repos_clonados"
OUTPUT_DIR = BASE_DIR / "data" / "ck_results"
SUMMARY_CSV = BASE_DIR / "data" / "metricas_ck_1000repos.csv"
PROGRESS_FILE = BASE_DIR / "data" / "progresso.json"
ERRORS_LOG = BASE_DIR / "data" / "erros.log"


def log_error(repo_name, stage, message):
    """Registra erros em arquivo de log."""
    with open(ERRORS_LOG, "a", encoding="utf-8") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{ts}] {repo_name} | {stage} | {message}\n")


def check_prerequisites():
    """Verifica se Java e Git estao disponiveis."""
    for cmd in ["java", "git"]:
        try:
            subprocess.run([cmd, "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"ERRO: '{cmd}' nao encontrado no PATH.")
            sys.exit(1)

    if not CK_JAR.exists():
        print(f"ERRO: CK JAR nao encontrado em {CK_JAR}")
        print("Baixe com: python -c \"import urllib.request; "
              "urllib.request.urlretrieve("
              "'https://repo1.maven.org/maven2/com/github/mauricioaniche/ck/0.7.0/"
              "ck-0.7.0-jar-with-dependencies.jar', 'tools/ck-0.7.0-jar-with-dependencies.jar')\"")
        sys.exit(1)

    print("[OK] Pre-requisitos verificados (Java, Git, CK JAR)")


def load_progress():
    """Carrega progresso salvo (repos ja processados)."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"processed": [], "results": []}


def save_progress(progress):
    """Salva progresso atual para permitir resume."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def clone_repo(repo_name, clone_path):
    """Clona um repositorio do GitHub (shallow clone)."""
    if clone_path.exists():
        return True

    url = f"https://github.com/{repo_name}.git"
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", "--single-branch", url, str(clone_path)],
            capture_output=True, check=True, timeout=300
        )
        return True
    except subprocess.TimeoutExpired:
        log_error(repo_name, "clone", "Timeout (300s)")
        return False
    except subprocess.CalledProcessError as e:
        msg = e.stderr.decode(errors="replace")[:200]
        log_error(repo_name, "clone", msg)
        return False


def run_ck(clone_path, output_path):
    """Executa o CK no repositorio clonado."""
    output_path.mkdir(parents=True, exist_ok=True)
    class_csv = output_path / "class.csv"
    if class_csv.exists():
        return True

    try:
        subprocess.run(
            ["java", "-jar", str(CK_JAR), str(clone_path),
             "false", "0", "false", str(output_path) + "/"],
            capture_output=True, check=True, timeout=900
        )
        return True
    except subprocess.TimeoutExpired:
        log_error(str(clone_path), "ck", "Timeout (900s)")
        return False
    except subprocess.CalledProcessError as e:
        msg = e.stderr.decode(errors="replace")[:200]
        log_error(str(clone_path), "ck", msg)
        return False


def summarize_ck_class(ck_class_csv):
    """Le o class.csv e calcula mediana, media e desvio padrao de CBO, DIT, LCOM + LOC."""
    if not ck_class_csv.exists():
        return None

    try:
        df = pd.read_csv(ck_class_csv)
    except Exception:
        return None

    if len(df) == 0:
        return None

    metrics = ["cbo", "dit", "lcom"]
    available = [m for m in metrics if m in df.columns]
    if not available:
        return None

    summary = {}
    for m in available:
        col = df[m].dropna()
        if len(col) == 0:
            continue
        summary[f"{m}_media"] = round(col.mean(), 4)
        summary[f"{m}_mediana"] = round(col.median(), 4)
        summary[f"{m}_desvio"] = round(col.std(), 4)

    if "loc" in df.columns:
        summary["loc_total"] = int(df["loc"].sum())
        summary["loc_media"] = round(df["loc"].mean(), 4)
        summary["loc_mediana"] = round(df["loc"].median(), 4)

    # Linhas de comentario: campo nao direto no CK class.csv,
    # mas podemos usar 'lcom' como proxy ou somar do method.csv
    # O CK nao gera "comment lines" diretamente - usamos LOC como metrica de tamanho

    if "totalMethodsQty" in df.columns:
        summary["total_methods"] = int(df["totalMethodsQty"].sum())

    summary["total_classes"] = len(df)
    return summary


def process_repo(repo_name, repo_info, progress):
    """Processa um unico repositorio com suporte a resume."""
    if repo_name in progress["processed"]:
        return None  # ja processado

    safe_name = repo_name.replace("/", "_")
    clone_path = CLONE_DIR / safe_name
    ck_output_path = OUTPUT_DIR / safe_name

    # 1. Clone
    if not clone_repo(repo_name, clone_path):
        progress["processed"].append(repo_name)
        return None

    # 2. Executar CK
    if not run_ck(clone_path, ck_output_path):
        # Limpar clone com erro
        shutil.rmtree(clone_path, ignore_errors=True)
        progress["processed"].append(repo_name)
        return None

    # 3. Sumarizar resultados
    class_csv = ck_output_path / "class.csv"
    summary = summarize_ck_class(class_csv)

    # Limpar clone para economizar espaco
    shutil.rmtree(clone_path, ignore_errors=True)

    if summary is None:
        progress["processed"].append(repo_name)
        return None

    summary["nome"] = repo_name
    summary["estrelas"] = repo_info.get("estrelas", 0)
    summary["idade_anos"] = repo_info.get("idade_anos", 0)
    summary["releases"] = repo_info.get("releases", 0)

    progress["processed"].append(repo_name)
    progress["results"].append(summary)
    return summary


def save_final_csv(progress):
    """Salva CSV final com todos os resultados."""
    if not progress["results"]:
        return

    df = pd.DataFrame(progress["results"])
    cols_order = [
        "nome", "estrelas", "idade_anos", "releases",
        "total_classes", "loc_total", "loc_media", "loc_mediana", "total_methods",
        "cbo_media", "cbo_mediana", "cbo_desvio",
        "dit_media", "dit_mediana", "dit_desvio",
        "lcom_media", "lcom_mediana", "lcom_desvio",
    ]
    cols_available = [c for c in cols_order if c in df.columns]
    df = df[cols_available]
    df.to_csv(SUMMARY_CSV, index=False)
    return df


def main():
    parser = argparse.ArgumentParser(description="Lab02S02 - Automacao: Clone + CK Metrics (1000 repos)")
    parser.add_argument("--limit", type=int, default=None, help="Numero de repos para processar")
    parser.add_argument("--repo", type=str, default=None, help="Repo especifico (owner/name)")
    parser.add_argument("--reset", action="store_true", help="Resetar progresso e recomecar")
    args = parser.parse_args()

    print("=" * 60)
    print("Lab02S02 - Automacao: Clone + Coleta de Metricas CK")
    print("=" * 60)

    check_prerequisites()

    if not REPOS_CSV.exists():
        print(f"\nERRO: CSV nao encontrado: {REPOS_CSV}")
        print("Execute primeiro o notebook 01-coletar-repos-java.ipynb")
        sys.exit(1)

    # Carregar progresso (resume)
    if args.reset and PROGRESS_FILE.exists():
        PROGRESS_FILE.unlink()
        print("[RESET] Progresso apagado.")

    progress = load_progress()
    already_done = len(progress["processed"])

    # Carregar repos
    repos_df = pd.read_csv(REPOS_CSV)
    if args.repo:
        repos_df = repos_df[repos_df["nome"] == args.repo]
    if args.limit:
        repos_df = repos_df.head(args.limit)

    total = len(repos_df)
    pending = total - already_done
    print(f"\nTotal de repos: {total}")
    print(f"Ja processados: {already_done}")
    print(f"Pendentes: {max(0, pending)}")
    print(f"Com resultado OK: {len(progress['results'])}")

    CLONE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Processar cada repo
    success_count = len(progress["results"])
    start_time = time.time()

    for idx, row in repos_df.iterrows():
        repo_name = row["nome"]
        if repo_name in progress["processed"]:
            continue

        i = len(progress["processed"]) + 1
        print(f"\n[{i}/{total}] {repo_name}")

        result = process_repo(repo_name, row.to_dict(), progress)

        if result:
            success_count += 1
            print(f"  [OK] classes={result.get('total_classes', '?')}, "
                  f"CBO={result.get('cbo_media', '?')}, "
                  f"DIT={result.get('dit_media', '?')}, "
                  f"LCOM={result.get('lcom_media', '?')}")
        else:
            if repo_name in progress["processed"]:
                print(f"  [FALHA] Ver {ERRORS_LOG}")

        # Salvar progresso a cada 5 repos
        if len(progress["processed"]) % 5 == 0:
            save_progress(progress)
            save_final_csv(progress)

        # Estimativa de tempo
        elapsed = time.time() - start_time
        done_this_session = len(progress["processed"]) - already_done
        if done_this_session > 0:
            avg = elapsed / done_this_session
            remaining = total - len(progress["processed"])
            eta_min = (avg * remaining) / 60
            print(f"  [ETA] ~{eta_min:.0f} min restantes ({remaining} repos)")

    # Salvar final
    save_progress(progress)
    df_final = save_final_csv(progress)

    print(f"\n{'=' * 60}")
    print(f"CONCLUIDO!")
    print(f"Total processados: {len(progress['processed'])}/{total}")
    print(f"Com resultado OK: {success_count}")
    print(f"CSV salvo em: {SUMMARY_CSV}")

    if df_final is not None:
        print(f"\nResumo das metricas ({len(df_final)} repos):")
        for col in ["cbo_media", "dit_media", "lcom_media", "loc_total"]:
            if col in df_final.columns:
                print(f"  {col}: media={df_final[col].mean():.2f}, "
                      f"mediana={df_final[col].median():.2f}")


if __name__ == "__main__":
    main()
