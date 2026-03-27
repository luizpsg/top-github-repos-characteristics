"""
Lab02S01 - Script de Automacao: Clone de Repositorios + Coleta de Metricas CK

Uso:
    python 02-automacao-clone-ck.py                     # processa todos os repos do CSV
    python 02-automacao-clone-ck.py --limit 1           # processa apenas 1 repo (demo)
    python 02-automacao-clone-ck.py --repo owner/name   # processa um repo especifico

Pre-requisitos:
    - Java 8+ instalado (java no PATH)
    - Git instalado (git no PATH)
    - Arquivo data/repos_java_top1000.csv gerado pelo notebook 01
    - ck-0.7.0-jar-with-dependencies.jar na pasta tools/
      (baixar de: https://repo1.maven.org/maven2/com/github/mauricioaniche/ck/0.7.0/ck-0.7.0-jar-with-dependencies.jar)
"""

import os
import sys
import csv
import subprocess
import shutil
import argparse
import time
from pathlib import Path

# --- Configuracao ---
BASE_DIR = Path(__file__).resolve().parent
REPOS_CSV = BASE_DIR / "data" / "repos_java_top1000.csv"
TOOLS_DIR = BASE_DIR / "tools"
CK_JAR = TOOLS_DIR / "ck-0.7.0-jar-with-dependencies.jar"
CLONE_DIR = BASE_DIR / "data" / "repos_clonados"
OUTPUT_DIR = BASE_DIR / "data" / "ck_results"
SUMMARY_CSV = BASE_DIR / "data" / "metricas_ck_sumarizadas.csv"


def check_prerequisites():
    """Verifica se Java e Git estao disponiveis."""
    for cmd in ["java", "git"]:
        try:
            subprocess.run([cmd, "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"ERRO: '{cmd}' nao encontrado no PATH. Instale antes de continuar.")
            sys.exit(1)

    if not CK_JAR.exists():
        print(f"ERRO: CK JAR nao encontrado em {CK_JAR}")
        print("Baixe de: https://github.com/mauricioaniche/ck/releases")
        print(f"Coloque o arquivo em: {TOOLS_DIR}/")
        sys.exit(1)

    print("[OK] Pre-requisitos verificados (Java, Git, CK JAR)")


def clone_repo(repo_name, clone_path):
    """Clona um repositorio do GitHub (shallow clone para economizar espaco)."""
    if clone_path.exists():
        print(f"  [skip] Repo ja clonado: {clone_path}")
        return True

    url = f"https://github.com/{repo_name}.git"
    print(f"  Clonando {repo_name}...")
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", url, str(clone_path)],
            capture_output=True, check=True, timeout=300
        )
        return True
    except subprocess.TimeoutExpired:
        print(f"  [ERRO] Timeout ao clonar {repo_name}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  [ERRO] Falha ao clonar {repo_name}: {e.stderr.decode()[:200]}")
        return False


def run_ck(clone_path, output_path):
    """Executa o CK no repositorio clonado."""
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"  Executando CK...")
    try:
        subprocess.run(
            ["java", "-jar", str(CK_JAR), str(clone_path), "false", "0", "false", str(output_path) + "/"],
            capture_output=True, check=True, timeout=600
        )
        return True
    except subprocess.TimeoutExpired:
        print(f"  [ERRO] Timeout ao executar CK")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  [ERRO] Falha ao executar CK: {e.stderr.decode()[:200]}")
        return False


def summarize_ck_class(ck_class_csv):
    """Le o class.csv gerado pelo CK e calcula mediana, media e desvio padrao de CBO, DIT, LCOM."""
    import pandas as pd

    if not ck_class_csv.exists():
        print(f"  [AVISO] class.csv nao encontrado: {ck_class_csv}")
        return None

    df = pd.read_csv(ck_class_csv)
    metrics = ["cbo", "dit", "lcom"]
    available = [m for m in metrics if m in df.columns]

    if not available:
        print(f"  [AVISO] Metricas CBO/DIT/LCOM nao encontradas no CSV")
        return None

    summary = {}
    for m in available:
        col = df[m].dropna()
        summary[f"{m}_media"] = round(col.mean(), 4)
        summary[f"{m}_mediana"] = round(col.median(), 4)
        summary[f"{m}_desvio"] = round(col.std(), 4)

    # LOC e comentarios (se disponiveis)
    if "loc" in df.columns:
        summary["loc_total"] = int(df["loc"].sum())
    if "totalMethodsQty" in df.columns:
        summary["total_methods"] = int(df["totalMethodsQty"].sum())

    summary["total_classes"] = len(df)
    return summary


def load_repos(csv_path, limit=None, specific_repo=None):
    """Carrega a lista de repositorios do CSV."""
    import pandas as pd
    df = pd.read_csv(csv_path)

    if specific_repo:
        df = df[df["nome"] == specific_repo]
        if df.empty:
            print(f"ERRO: Repositorio '{specific_repo}' nao encontrado no CSV")
            sys.exit(1)

    if limit:
        df = df.head(limit)

    return df


def process_repo(repo_name, repo_info):
    """Processa um unico repositorio: clone + CK + sumarizacao."""
    safe_name = repo_name.replace("/", "_")
    clone_path = CLONE_DIR / safe_name
    ck_output_path = OUTPUT_DIR / safe_name

    # 1. Clone
    if not clone_repo(repo_name, clone_path):
        return None

    # 2. Executar CK
    if not run_ck(clone_path, ck_output_path):
        return None

    # 3. Sumarizar resultados
    class_csv = ck_output_path / "class.csv"
    summary = summarize_ck_class(class_csv)

    if summary is None:
        return None

    # Adicionar info do repositorio
    summary["nome"] = repo_name
    summary["estrelas"] = repo_info.get("estrelas", 0)
    summary["idade_anos"] = repo_info.get("idade_anos", 0)
    summary["releases"] = repo_info.get("releases", 0)

    return summary


def main():
    parser = argparse.ArgumentParser(description="Automacao: Clone + CK Metrics")
    parser.add_argument("--limit", type=int, default=None, help="Numero de repos para processar")
    parser.add_argument("--repo", type=str, default=None, help="Repo especifico (owner/name)")
    parser.add_argument("--keep-clones", action="store_true", help="Manter repos clonados apos analise")
    args = parser.parse_args()

    print("=" * 60)
    print("Lab02S01 - Automacao: Clone + Coleta de Metricas CK")
    print("=" * 60)

    # Verificar pre-requisitos
    check_prerequisites()

    # Verificar CSV de repos
    if not REPOS_CSV.exists():
        print(f"\nERRO: CSV de repositorios nao encontrado: {REPOS_CSV}")
        print("Execute primeiro o notebook 01-coletar-repos-java.ipynb")
        sys.exit(1)

    # Carregar repos
    repos_df = load_repos(REPOS_CSV, limit=args.limit, specific_repo=args.repo)
    total = len(repos_df)
    print(f"\nRepositorios a processar: {total}")

    # Criar diretorios
    CLONE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Processar cada repo
    results = []
    for idx, row in repos_df.iterrows():
        repo_name = row["nome"]
        print(f"\n[{len(results) + 1}/{total}] {repo_name}")

        result = process_repo(repo_name, row.to_dict())
        if result:
            results.append(result)
            print(f"  [OK] CBO media={result.get('cbo_media', 'N/A')}, "
                  f"DIT media={result.get('dit_media', 'N/A')}, "
                  f"LCOM media={result.get('lcom_media', 'N/A')}")

        # Limpar clone para economizar espaco (a menos que --keep-clones)
        if not args.keep_clones:
            safe_name = repo_name.replace("/", "_")
            clone_path = CLONE_DIR / safe_name
            if clone_path.exists():
                shutil.rmtree(clone_path, ignore_errors=True)
                print(f"  [clean] Clone removido")

    # Salvar resultados sumarizados
    if results:
        import pandas as pd
        df_results = pd.DataFrame(results)
        # Reordenar colunas
        cols_order = ["nome", "estrelas", "idade_anos", "releases",
                      "total_classes", "loc_total", "total_methods",
                      "cbo_media", "cbo_mediana", "cbo_desvio",
                      "dit_media", "dit_mediana", "dit_desvio",
                      "lcom_media", "lcom_mediana", "lcom_desvio"]
        cols_available = [c for c in cols_order if c in df_results.columns]
        df_results = df_results[cols_available]

        df_results.to_csv(SUMMARY_CSV, index=False)
        print(f"\n{'=' * 60}")
        print(f"Resultado salvo em: {SUMMARY_CSV}")
        print(f"Repositorios processados com sucesso: {len(results)}/{total}")
        print(df_results.to_string(index=False))
    else:
        print("\nNenhum repositorio processado com sucesso.")


if __name__ == "__main__":
    main()
