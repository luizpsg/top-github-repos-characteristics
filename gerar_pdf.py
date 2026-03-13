"""
Gera o relatório final do Lab01 em PDF com formato acadêmico,
incluindo gráficos, tabelas e todas as seções do relatório Markdown.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib import colors

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

OUTPUT_PDF = os.path.join(
    REPORTS_DIR,
    f"relatorio_final_lab01_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
)

# ─── Styles ───────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

DARK = HexColor("#1a1a2e")
ACCENT = HexColor("#16213e")
LINK_COLOR = HexColor("#0066cc")

style_title = ParagraphStyle(
    "ArticleTitle", parent=styles["Title"],
    fontSize=18, leading=22, alignment=TA_CENTER,
    spaceAfter=6, textColor=DARK, fontName="Helvetica-Bold"
)

style_subtitle = ParagraphStyle(
    "ArticleSubtitle", parent=styles["Normal"],
    fontSize=11, leading=14, alignment=TA_CENTER,
    spaceAfter=4, textColor=HexColor("#444444"), fontName="Helvetica"
)

style_h1 = ParagraphStyle(
    "H1", parent=styles["Heading1"],
    fontSize=14, leading=18, spaceBefore=18, spaceAfter=8,
    textColor=DARK, fontName="Helvetica-Bold"
)

style_h2 = ParagraphStyle(
    "H2", parent=styles["Heading2"],
    fontSize=12, leading=15, spaceBefore=12, spaceAfter=6,
    textColor=ACCENT, fontName="Helvetica-Bold"
)

style_body = ParagraphStyle(
    "BodyText2", parent=styles["BodyText"],
    fontSize=10, leading=14, alignment=TA_JUSTIFY,
    spaceAfter=6, fontName="Helvetica"
)

style_body_bold = ParagraphStyle(
    "BodyBold", parent=style_body,
    fontName="Helvetica-Bold"
)

style_bullet = ParagraphStyle(
    "Bullet2", parent=style_body,
    leftIndent=18, bulletIndent=6, spaceBefore=2, spaceAfter=2
)

style_caption = ParagraphStyle(
    "Caption", parent=styles["Normal"],
    fontSize=9, leading=11, alignment=TA_CENTER,
    spaceAfter=10, textColor=HexColor("#555555"), fontName="Helvetica-Oblique"
)

style_ref = ParagraphStyle(
    "Reference", parent=style_body,
    fontSize=9, leading=12, leftIndent=18, firstLineIndent=-18
)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def heading(text, level=1):
    return Paragraph(text, style_h1 if level == 1 else style_h2)


def body(text):
    return Paragraph(text, style_body)


def bold_body(text):
    return Paragraph(text, style_body_bold)


def bullet(text):
    return Paragraph(f"• {text}", style_bullet)


def spacer(h=6):
    return Spacer(1, h)


def hr():
    return HRFlowable(width="100%", thickness=0.5, color=HexColor("#cccccc"),
                      spaceBefore=8, spaceAfter=8)


def make_table(header, rows, col_widths=None):
    """Create a styled table."""
    data = [header] + rows
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#bdc3c7")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, HexColor("#f8f9fa")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def add_figure(story, filename, caption, width=15 * cm, max_height=18 * cm):
    """Add a chart image with caption, constraining to page dimensions."""
    from PIL import Image as PILImage
    path = os.path.join(CHARTS_DIR, filename)
    if os.path.exists(path):
        pil_img = PILImage.open(path)
        iw, ih = pil_img.size
        aspect = ih / iw
        final_w = width
        final_h = width * aspect
        if final_h > max_height:
            final_h = max_height
            final_w = max_height / aspect
        img = Image(path, width=final_w, height=final_h)
        img.hAlign = "CENTER"
        story.append(spacer(6))
        story.append(img)
        story.append(Paragraph(caption, style_caption))
    else:
        story.append(body(f"<i>[Figura não encontrada: {filename}]</i>"))


# ─── Build Document ──────────────────────────────────────────────────────────
def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PDF, pagesize=A4,
        leftMargin=2.5 * cm, rightMargin=2.5 * cm,
        topMargin=2.5 * cm, bottomMargin=2.5 * cm,
        title="Relatório Final — Lab01",
        author="Laboratório de Experimentação de Software — PUC Minas"
    )

    story = []

    # ── Title Page ────────────────────────────────────────────────────────
    story.append(spacer(60))
    story.append(Paragraph(
        "Características de Repositórios Populares do GitHub",
        style_title
    ))
    story.append(Paragraph(
        "Lab01 — Laboratório de Experimentação de Software",
        style_subtitle
    ))
    story.append(spacer(12))
    story.append(Paragraph(
        "Engenharia de Software — PUC Minas",
        style_subtitle
    ))
    story.append(Paragraph(
        f"Data: {datetime.now().strftime('%d/%m/%Y')}",
        style_subtitle
    ))
    story.append(spacer(30))
    story.append(hr())

    # ══════════════════════════════════════════════════════════════════════
    # 1. INTRODUÇÃO
    # ══════════════════════════════════════════════════════════════════════
    story.append(heading("1. Introdução"))

    story.append(heading("1.1 Contextualização", 2))
    story.append(body(
        "O GitHub é a maior plataforma de hospedagem de código-fonte do mundo, "
        "reunindo milhões de repositórios open-source. O número de estrelas "
        "(<i>stars</i>) é amplamente utilizado como indicador de popularidade e "
        "relevância de um projeto pela comunidade. Compreender as características "
        "dos repositórios mais populares permite identificar padrões que contribuem "
        "para o sucesso e a sustentabilidade de projetos open-source."
    ))

    story.append(heading("1.2 Problema foco do experimento", 2))
    story.append(body(
        "Quais são as principais características dos repositórios open-source mais "
        "populares do GitHub em termos de maturidade, contribuição externa, frequência "
        "de releases e atualizações, linguagens de programação e manutenção de issues?"
    ))

    story.append(heading("1.3 Questões de Pesquisa", 2))
    rqs = make_table(
        ["RQ", "Pergunta", "Métrica"],
        [
            ["01", "Sistemas populares são maduros/antigos?", "Idade do repositório (dias)"],
            ["02", "Recebem muita contribuição externa?", "Total de PRs aceitas (merged)"],
            ["03", "Lançam releases com frequência?", "Total de releases"],
            ["04", "São atualizados com frequência?", "Tempo até última atualização (dias)"],
            ["05", "São escritos nas linguagens mais populares?", "Linguagem primária"],
            ["06", "Possuem alto percentual de issues fechadas?", "Razão issues fechadas / total"],
            ["07", "Linguagens populares recebem mais contribuição?", "PRs, releases e update por grupo"],
        ],
        col_widths=[1.2 * cm, 8 * cm, 6.5 * cm]
    )
    story.append(rqs)
    story.append(spacer(8))

    story.append(heading("1.4 Hipóteses", 2))
    hipoteses = [
        "<b>H1 (RQ01):</b> A mediana de idade dos repositórios populares é de <b>pelo menos 5 anos</b> (1.825 dias), pois leva tempo para acumular estrelas e construir comunidade.",
        "<b>H2 (RQ02):</b> A mediana de PRs aceitas dos repositórios populares é de <b>pelo menos 500</b>, já que a alta visibilidade atrai colaboradores.",
        "<b>H3 (RQ03):</b> A mediana de releases dos repositórios populares é de <b>pelo menos 20</b>, mantendo o projeto ativo e organizado.",
        "<b>H4 (RQ04):</b> A mediana de dias desde a última atualização dos repositórios populares é de <b>no máximo 1 dia</b>, indicando manutenção praticamente diária.",
        "<b>H5 (RQ05):</b> <b>Mais de 50%</b> dos repositórios populares (com linguagem definida) são escritos nas linguagens mais populares (TypeScript, Python, JavaScript).",
        "<b>H6 (RQ06):</b> A mediana da razão de issues fechadas dos repositórios populares é <b>acima de 70%</b>, indicando manutenção ativa e responsiva.",
        "<b>H7 (RQ07):</b> Sistemas em linguagens do Top 3 Octoverse apresentam <b>mediana de PRs aceitas e releases pelo menos 20% superior</b> ao grupo de outras linguagens.",
    ]
    for h in hipoteses:
        story.append(bullet(h))

    story.append(heading("1.5 Objetivos", 2))
    story.append(bold_body("Objetivo principal:"))
    story.append(body(
        "Caracterizar os 1000 repositórios open-source mais populares do GitHub por meio de "
        "métricas extraídas via API GraphQL, respondendo às 7 questões de pesquisa formuladas."
    ))
    story.append(bold_body("Objetivos específicos:"))
    obj_especificos = [
        "Avaliar a maturidade dos repositórios populares através da idade.",
        "Quantificar a contribuição externa por meio de pull requests aceitas.",
        "Medir a frequência de releases e atualizações.",
        "Identificar as linguagens de programação predominantes.",
        "Calcular a taxa de resolução de issues.",
        "Comparar métricas de atividade entre repositórios de linguagens populares e outras.",
    ]
    for o in obj_especificos:
        story.append(bullet(o))

    # ══════════════════════════════════════════════════════════════════════
    # 2. METODOLOGIA
    # ══════════════════════════════════════════════════════════════════════
    story.append(heading("2. Metodologia"))

    story.append(heading("2.1 Passo a passo do experimento", 2))
    passos = [
        "<b>Configuração:</b> Obtenção de Personal Access Token (PAT) para acesso à API do GitHub.",
        "<b>Construção da query:</b> Elaboração de query GraphQL para buscar repositórios ordenados por estrelas.",
        "<b>Coleta paginada:</b> Requisições automáticas paginadas (lotes de 10) com intervalo de 3s e retry exponencial.",
        "<b>Montagem do dataset:</b> Construção de DataFrame pandas com métricas brutas e derivadas.",
        "<b>Análise exploratória:</b> Estatísticas descritivas (medianas, quartis, desvio padrão) para cada RQ.",
        "<b>Visualização:</b> Gráficos (histogramas, boxplots, barras, scatter plots) com matplotlib e seaborn.",
        "<b>Teste estatístico:</b> Teste de Mann-Whitney U para comparação entre grupos de linguagem (RQ07).",
        "<b>Exportação:</b> Dados salvos em CSV e JSON; relatório gerado em Markdown e PDF.",
    ]
    for i, p in enumerate(passos, 1):
        story.append(bullet(f"{i}. {p}"))

    story.append(heading("2.2 Decisões", 2))
    decisoes = [
        "<b>Mediana</b> como medida central principal, por ser mais robusta a outliers — distribuições fortemente assimétricas.",
        "Classificação de <b>linguagens populares</b> baseada no GitHub Octoverse 2025: TypeScript, Python e JavaScript.",
        "Repositórios sem linguagem primária definida foram <b>excluídos</b> das análises de RQ05 e RQ07 (96 repositórios).",
        "Teste de <b>Mann-Whitney U</b> (não-paramétrico, bicaudal, α = 0.05) para verificar significância estatística na RQ07.",
    ]
    for d in decisoes:
        story.append(bullet(d))

    story.append(heading("2.3 Materiais utilizados", 2))
    materiais = [
        "<b>API:</b> GitHub GraphQL API v4",
        "<b>Linguagem:</b> Python 3",
        "<b>Bibliotecas:</b> requests, pandas, numpy, matplotlib, seaborn, scipy, tqdm",
        "<b>Ambiente:</b> Jupyter Notebook",
    ]
    for m in materiais:
        story.append(bullet(m))

    story.append(heading("2.4 Métricas e suas Unidades", 2))
    metricas_table = make_table(
        ["Métrica", "Unidade", "Descrição"],
        [
            ["idade_dias", "dias", "Data atual − data de criação do repositório"],
            ["prs_aceitas", "contagem", "Pull requests com estado MERGED"],
            ["releases", "contagem", "Total de releases publicadas"],
            ["dias_desde_update", "dias", "Data atual − data da última atualização"],
            ["razao_fechadas", "proporção (0–1)", "Issues fechadas ÷ total de issues"],
        ],
        col_widths=[3.5 * cm, 3.5 * cm, 8.7 * cm]
    )
    story.append(metricas_table)

    # ══════════════════════════════════════════════════════════════════════
    # 3. VISUALIZAÇÃO DOS RESULTADOS
    # ══════════════════════════════════════════════════════════════════════
    story.append(heading("3. Visualização dos Resultados"))

    story.append(heading("3.1 Estatísticas Descritivas Gerais", 2))
    stats_table = make_table(
        ["Métrica", "Mín", "Q1", "Mediana", "Q3", "Máx", "Desvio Padrão"],
        [
            ["Estrelas", "29 594", "34 344", "42 956", "62 580", "472 883", "46 453"],
            ["Idade (dias)", "33", "1 829", "3 061", "4 168", "6 538", "1 494"],
            ["PRs aceitas", "0", "174", "743", "3 198", "94 722", "9 869"],
            ["Releases", "0", "0", "40", "144", "1 000", "199"],
            ["Dias desde update", "0", "0", "0", "0", "1", "0,14"],
            ["Razão issues fechadas", "0,0000", "0,6782", "0,8676", "0,9584", "1,0000", "0,2571"],
        ],
        col_widths=[3.2 * cm, 1.8 * cm, 1.8 * cm, 2 * cm, 1.8 * cm, 2 * cm, 2.5 * cm]
    )
    story.append(stats_table)

    story.append(heading("3.2 Gráficos por Questão de Pesquisa", 2))

    # RQ01
    add_figure(story, "01_rq01_idade.png",
               "Figura 1 — Histograma e boxplot da idade dos repositórios (RQ01)")

    # RQ02
    add_figure(story, "02_rq02_prs.png",
               "Figura 2 — Distribuição de PRs aceitas em escala logarítmica e boxplot (RQ02)")

    # RQ03
    add_figure(story, "03_rq03_releases.png",
               "Figura 3 — Distribuição de releases e proporção com/sem releases (RQ03)")

    # RQ04
    add_figure(story, "04_rq04_update.png",
               "Figura 4 — Frequência de atualização dos repositórios (RQ04)")

    # RQ05
    add_figure(story, "05_rq05_linguagens.png",
               "Figura 5 — Top 15 linguagens e proporção por grupo (RQ05)")

    # RQ06
    add_figure(story, "06_rq06_issues.png",
               "Figura 6 — Distribuição e boxplot da razão de issues fechadas (RQ06)")

    # RQ07
    add_figure(story, "07_rq07_comparacao.png",
               "Figura 7 — Boxplots comparativos entre grupos de linguagem (RQ07)")

    add_figure(story, "07_rq07_barras.png",
               "Figura 8 — Barras agrupadas com medianas por grupo de linguagem (RQ07)")

    # Extras
    add_figure(story, "08_scatter_idade_prs.png",
               "Figura 9 — Scatter plot: idade vs PRs aceitas")

    add_figure(story, "09_metricas_por_linguagem.png",
               "Figura 10 — Boxplots de métricas para as Top 10 linguagens")

    add_figure(story, "00_correlacao.png",
               "Figura 11 — Matriz de correlação entre métricas")

    story.append(heading("3.3 RQ05 — Distribuição por Linguagem (Top 15)", 2))
    lang_table = make_table(
        ["Linguagem", "Repositórios"],
        [
            ["Python", "201"], ["TypeScript", "160"], ["JavaScript", "115"],
            ["Sem linguagem", "95"], ["Go", "76"], ["Rust", "54"],
            ["Java", "47"], ["C++", "46"], ["C", "25"],
            ["Jupyter Notebook", "23"], ["Shell", "21"], ["HTML", "18"],
            ["Ruby", "12"], ["C#", "11"], ["Kotlin", "10"],
        ],
        col_widths=[5 * cm, 4 * cm]
    )
    story.append(lang_table)
    story.append(spacer(4))
    story.append(body(
        "Dos 905 repositórios com linguagem definida, <b>476 (52,6%)</b> utilizam uma das "
        "3 linguagens mais populares do Octoverse 2025."
    ))

    story.append(heading("3.4 RQ07 — Comparação entre Grupos de Linguagem", 2))
    comp_table = make_table(
        ["Grupo", "PRs aceitas (med.)", "Releases (med.)", "Dias desde update (med.)"],
        [
            ["Top 3 Octoverse", "957", "64", "0"],
            ["Outras linguagens", "787", "43", "0"],
        ],
        col_widths=[4 * cm, 3.8 * cm, 3.5 * cm, 4.5 * cm]
    )
    story.append(comp_table)
    story.append(spacer(6))

    story.append(bold_body("Teste de Mann-Whitney U (α = 0,05):"))
    mann_table = make_table(
        ["Métrica", "Estatística U", "p-valor", "Significativo?"],
        [
            ["PRs aceitas", "106 307", "0,284258", "Não"],
            ["Releases", "111 794", "0,013022", "Sim"],
            ["Dias desde update", "102 819", "0,424034", "Não"],
        ],
        col_widths=[4 * cm, 3.5 * cm, 3 * cm, 3 * cm]
    )
    story.append(mann_table)

    # ══════════════════════════════════════════════════════════════════════
    # 4. DISCUSSÃO DOS RESULTADOS
    # ══════════════════════════════════════════════════════════════════════
    story.append(heading("4. Discussão dos Resultados"))

    story.append(heading("4.1 Confronto com as Questões de Pesquisa", 2))

    rq_discussions = [
        (
            "<b>RQ01 — Maturidade:</b>",
            "A mediana de idade é <b>3061 dias (~8,4 anos)</b>, com 85% dos repositórios tendo mais de "
            "3 anos. <b>Hipótese confirmada:</b> repositórios populares são, de fato, projetos maduros "
            "com histórico consolidado. Isso se explica pelo tempo necessário para acumular estrelas, "
            "construir comunidade e ganhar visibilidade orgânica."
        ),
        (
            "<b>RQ02 — Contribuição externa:</b>",
            "A mediana de <b>743 PRs aceitas</b> indica contribuição externa significativa, embora a "
            "distribuição seja extremamente assimétrica (média de 3954, desvio padrão de 9869). "
            "<b>Hipótese confirmada:</b> a visibilidade de fato atrai colaboradores, mas a intensidade "
            "varia muito — alguns projetos recebem dezenas de milhares de PRs, enquanto outros "
            "(tipicamente listas curadas) recebem poucas."
        ),
        (
            "<b>RQ03 — Releases:</b>",
            "A mediana de <b>40 releases</b> sugere adoção moderada de releases formais, com 29,0% dos "
            "repositórios sem nenhuma release. <b>Hipótese parcialmente confirmada:</b> muitos projetos "
            "populares (especialmente listas curadas, recursos educacionais e bibliotecas que usam "
            "distribuição via gerenciadores de pacotes) não utilizam o sistema de releases do GitHub."
        ),
        (
            "<b>RQ04 — Atualização:</b>",
            "A mediana de <b>0 dias</b> desde o último update, com 98,0% atualizados no mesmo dia da "
            "coleta. <b>Hipótese confirmada:</b> esses repositórios são mantidos com altíssima "
            "frequência, praticamente em tempo real."
        ),
        (
            "<b>RQ05 — Linguagens:</b>",
            "<b>52,6%</b> dos repositórios com linguagem definida usam TypeScript, Python ou JavaScript. "
            "Python e TypeScript lideram com representatividade praticamente igual. <b>Hipótese "
            "confirmada:</b> a maioria dos repositórios populares é escrita nas linguagens mais "
            "populares do ecossistema."
        ),
        (
            "<b>RQ06 — Issues fechadas:</b>",
            "A mediana da razão de issues fechadas é <b>0,8676 (86,8%)</b>, com 73,1% dos repositórios "
            "acima de 70%. <b>Hipótese confirmada:</b> a maioria dos projetos populares mantém uma taxa "
            "elevada de resolução de issues, indicando manutenção ativa e responsiva."
        ),
        (
            "<b>RQ07 — Linguagens populares vs. outras:</b>",
            "Repositórios em linguagens do <b>Top 3 Octoverse</b> apresentam medianas superiores tanto em PRs aceitas "
            "quanto em releases. O teste de Mann-Whitney U indica se essas diferenças são estatisticamente "
            "significativas (ver tabela acima). Ambos os grupos apresentam mediana de 0 dias desde o último update. "
            "<b>Hipótese parcialmente confirmada:</b> linguagens populares correlacionam com mais atividade "
            "colaborativa, mas a frequência de atualização é uniformemente alta."
        ),
    ]
    for title, text in rq_discussions:
        story.append(body(title))
        story.append(body(text))
        story.append(spacer(4))

    story.append(heading("4.2 Insights", 2))
    insights = [
        "<b>Maturidade e popularidade andam juntas</b> — a mediana de ~8 anos indica que projetos "
        "precisam de tempo significativo para atingir alto número de estrelas.",
        "<b>Distribuições long-tail</b> — PRs, releases e issues apresentam distribuições extremamente "
        "assimétricas. A mediana é muito mais representativa que a média.",
        "<b>Listas curadas são um fenômeno</b> — os 96 repositórios sem linguagem definida são quase "
        "todos \"awesome lists\" e recursos educacionais, indicando que conteúdo curado é tão valorizado "
        "quanto software.",
        "<b>Atualização quase em tempo real</b> — 98,0% dos repositórios foram atualizados no mesmo "
        "dia da coleta.",
        "<b>A API limita releases a 1000</b> — 17 repositórios atingiram o limite da API GraphQL, "
        "sugerindo que o valor real pode ser ainda maior.",
    ]
    for i, ins in enumerate(insights, 1):
        story.append(bullet(f"{i}. {ins}"))

    story.append(heading("4.3 Limitações", 2))
    limitacoes = [
        "O campo <i>releases</i> da API retorna no máximo 1000, podendo subestimar projetos muito ativos.",
        "A data de \"última atualização\" (<i>updatedAt</i>) pode ser afetada por atividades automáticas "
        "(bots, CI/CD), não apenas contribuições humanas.",
        "A contagem de PRs aceitas inclui PRs de qualquer colaborador (incluindo maintainers), não "
        "apenas contribuições externas.",
        "A amostra é limitada aos 1000 repositórios mais estrelados, não representando o universo "
        "completo do GitHub.",
    ]
    for lim in limitacoes:
        story.append(bullet(lim))

    # ══════════════════════════════════════════════════════════════════════
    # 5. CONCLUSÃO
    # ══════════════════════════════════════════════════════════════════════
    story.append(heading("5. Conclusão"))

    story.append(heading("5.1 Resultado conclusivo", 2))
    story.append(body(
        "Os 1000 repositórios mais populares do GitHub são, em sua grande maioria, "
        "<b>projetos maduros</b> (mediana de ~8 anos), <b>ativamente mantidos</b> "
        "(atualizados diariamente), com <b>contribuição externa expressiva</b> "
        "(mediana de 743 PRs aceitas) e <b>alta taxa de resolução de issues</b> (86,8%). "
        "Mais da metade (52,6%) utiliza linguagens do Top 3 do GitHub Octoverse 2025 "
        "(TypeScript, Python, JavaScript)."
    ))
    story.append(body(
        "Das 7 hipóteses formuladas, <b>6 foram confirmadas</b> e <b>1 foi parcialmente "
        "confirmada</b> (H3 sobre releases). A principal surpresa foi a alta proporção de "
        "repositórios sem releases formais, revelando que popularidade não implica "
        "necessariamente em adoção de práticas de versionamento via releases do GitHub."
    ))

    story.append(heading("5.2 Tomada de decisão", 2))
    story.append(body("Os dados sugerem que, para maximizar a popularidade de um projeto open-source:"))
    decisoes_finais = [
        "Investir em <b>manutenção constante</b> (atualizações frequentes e resolução ágil de issues).",
        "Facilitar e incentivar <b>contribuições externas</b> via PRs.",
        "Considerar linguagens com <b>comunidades grandes</b> (TypeScript, Python, JavaScript).",
        "A adoção de releases formais é uma boa prática, mas não é determinante para popularidade.",
    ]
    for d in decisoes_finais:
        story.append(bullet(d))

    story.append(heading("5.3 Sugestões futuras", 2))
    sugestoes = [
        "Incorporar <b>análise temporal</b> (evolução das métricas ao longo do tempo via snapshots periódicos).",
        "Investigar a correlação entre <b>número de contribuidores únicos</b> e popularidade.",
        "Analisar o impacto de <b>licenças open-source</b> na popularidade.",
        "Estratificar a amostra por <b>domínio</b> (web, data science, DevOps, mobile, etc.).",
        "Incluir métricas de <b>qualidade de código</b> (cobertura de testes, CI/CD) para complementar a análise.",
    ]
    for s in sugestoes:
        story.append(bullet(s))

    story.append(heading("5.4 Referências", 2))
    refs = [
        "GitHub Octoverse 2025. <i>A new developer joins GitHub every second as AI leads TypeScript "
        "to #1</i>. Disponível em: https://github.blog/news-insights/octoverse/",
        "Munaiah, N. et al. (2017). <i>Curating GitHub for Engineered Software Projects</i>. "
        "Empirical Software Engineering.",
        "Kalliamvakou, E. et al. (2014). <i>The Promises and Perils of Mining GitHub</i>. MSR 2014.",
    ]
    for r in refs:
        story.append(Paragraph(r, style_ref))
        story.append(spacer(2))

    # ── Build ─────────────────────────────────────────────────────────────
    doc.build(story)
    print(f"PDF gerado com sucesso: {OUTPUT_PDF}")
    return OUTPUT_PDF


if __name__ == "__main__":
    build_pdf()
