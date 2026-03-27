# Lab 02 - Sprint 1: Análise de Qualidade de Repositórios Java

Estudo empírico que investiga a relação entre características de repositórios Java populares no GitHub (popularidade, maturidade, atividade e tamanho) e métricas de qualidade de código baseadas no conjunto CK (Chidamber & Kemerer).

## Questões de Pesquisa

| RQ  | Pergunta                                 | Métrica de Processo       | Métrica de Qualidade |
| :-: | ---------------------------------------- | ------------------------- | -------------------- |
| 01  | Repositórios populares são bem escritos? | Stars                     | CBO, DIT, LCOM       |
| 02  | Repositórios maduros são bem escritos?   | Idade (anos)              | CBO, DIT, LCOM       |
| 03  | Repositórios ativos são bem escritos?    | Nº de releases            | CBO, DIT, LCOM       |
| 04  | Repositórios grandes são bem escritos?   | LOC, Linhas de comentário | CBO, DIT, LCOM       |

### Métricas CK utilizadas

- **CBO** (Coupling Between Objects) — Quantidade de classes acopladas a uma classe. Valores altos indicam alto acoplamento.
- **DIT** (Depth of Inheritance Tree) — Profundidade máxima na árvore de herança. Valores altos indicam hierarquias complexas.
- **LCOM** (Lack of Cohesion of Methods) — Mede a coesão dos métodos de uma classe. Valores altos indicam baixa coesão.

## Estrutura do Projeto

```
sprint-1/
├── 01-coletar-repos-java.ipynb        # Coleta dos top 1000 repos Java via GitHub API
├── 02-automacao-clone-ck.py            # Automação: clone + análise CK em lote
├── 03-demo-ck-1-repo.ipynb             # Demonstração do pipeline em 1 repositório
├── tools/
│   └── ck-0.7.0-jar-with-dependencies.jar  # Ferramenta CK para métricas de código
├── data/
│   ├── repos_java_top1000.csv          # Dataset: 1000 repos Java mais populares
│   ├── repos_java_top1000.json         # Mesmo dataset em JSON
│   ├── metricas_ck_demo_1repo.csv      # Resultado demo (java-design-patterns)
│   ├── ck_class_raw_iluwatar_java-design-patterns.csv  # Métricas brutas por classe
│   └── ck_results/                     # Resultados CK por repositório
└── .gitignore
```

## Pipeline de Execução

### Etapa 1 — Coleta de Repositórios

**Notebook:** `01-coletar-repos-java.ipynb`

Coleta os 1.000 repositórios Java mais populares do GitHub usando a API GraphQL. Extrai: nome, URL, stars, data de criação, idade, número de releases e uso de disco.

**Saída:** `data/repos_java_top1000.csv` e `data/repos_java_top1000.json`

### Etapa 2 — Análise CK em Lote

**Script:** `02-automacao-clone-ck.py`

Para cada repositório do dataset:

1. Faz clone raso (`depth=1`) para economizar espaço
2. Executa a ferramenta CK sobre o código-fonte
3. Calcula estatísticas sumarizadas (média, mediana, desvio padrão) de CBO, DIT e LCOM
4. Remove o clone após análise

**Saída:** `data/metricas_ck_sumarizadas.csv`

### Etapa 3 — Demonstração

**Notebook:** `03-demo-ck-1-repo.ipynb`

Demonstra o pipeline completo para um único repositório (`iluwatar/java-design-patterns`), incluindo clone, análise CK, parsing dos resultados e cálculo de estatísticas.

## Pré-requisitos

| Dependência    | Versão | Finalidade                       |
| -------------- | ------ | -------------------------------- |
| Python         | 3.8+   | Execução dos scripts e notebooks |
| Java (JRE/JDK) | 8+     | Execução da ferramenta CK        |
| Git            | 2.x+   | Clone dos repositórios           |
| Token GitHub   | —      | Autenticação na API GraphQL      |

### Bibliotecas Python

```
requests
pandas
jupyter
```

## Como Executar

### 1. Configurar token do GitHub

Crie um [Personal Access Token](https://github.com/settings/tokens) no GitHub e configure-o no notebook `01-coletar-repos-java.ipynb`.

### 2. Coletar repositórios

```bash
jupyter notebook 01-coletar-repos-java.ipynb
```

Execute todas as células para gerar o dataset com os 1.000 repositórios.

### 3. Rodar análise CK em lote

```bash
python 02-automacao-clone-ck.py
```

> **Atenção:** Este script clona e analisa múltiplos repositórios. A execução completa pode levar várias horas e requer espaço em disco temporário significativo.

### 4. (Opcional) Demonstração com 1 repositório

```bash
jupyter notebook 03-demo-ck-1-repo.ipynb
```

## Dados Coletados

- **1.000 repositórios Java** com mais de 100 stars
- Repositório mais popular: `Snailclimb/JavaGuide` (154.216 stars)
- Faixa de idade dos repositórios: ~3 a 16 anos
- Exemplo de análise: `java-design-patterns` — 1.988 classes analisadas

## Tecnologias

- **Python 3** — Coleta de dados, automação e análise
- **GitHub GraphQL API** — Coleta de metadados dos repositórios
- **CK Tool v0.7.0** — Cálculo de métricas de código orientado a objetos
- **Jupyter Notebook** — Exploração interativa e documentação do pipeline
- **pandas** — Manipulação e sumarização de dados

## Contexto Acadêmico

Este projeto faz parte do **Laboratório de Experimentação de Software**, disciplina que aplica métodos empíricos para investigar propriedades de sistemas de software em larga escala.
