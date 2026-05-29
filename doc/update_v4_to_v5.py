"""
Script para atualizar TCC_Modelo_Estrutural_Formatado_v4.docx → v5.
Alterações:
  1. Reescrever P22 (vermelho) com novo objetivo e separar imagem
  2. Remover P23 (nota vermelha sobre constrained-off)
  3. Substituir P28-P29 por seção sobre curtailment
  4. Remover duplicata P51 (features T1/T4)
  5. Atualizar metodologia (OPSD + perfil Brasil)
  6. Remover duplicata P64 (resumo estatístico)
  7. Atualizar resultados com dados reais
  8. Adicionar referências
  9. Inserir título/fonte na imagem nova
"""

import copy
import shutil
from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from lxml import etree


# --- Paths ---
BASE = Path(__file__).resolve().parent
SRC = BASE / "TCC_Modelo_Estrutural_Formatado_v4.docx"
DST = BASE / "TCC_Modelo_Estrutural_Formatado_v5.docx"
OLD = BASE / "_old"

doc = Document(str(SRC))
body = doc.element.body


# ── helpers ──────────────────────────────────────────────────────────
def set_paragraph_text(p, text, *, bold=False, color=None, size=None):
    """Clear all runs and set a single run with the given text."""
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    # Also remove any remaining w:r elements
    for r_elem in list(p._element.findall(qn('w:r'))):
        p._element.remove(r_elem)
    run = p.add_run(text)
    if bold:
        run.bold = True
    if color:
        run.font.color.rgb = color
    if size:
        run.font.size = size
    return run


def clear_paragraph_text_keep_images(p):
    """Remove text runs but keep drawing/image elements."""
    for r_elem in list(p._element.findall(qn('w:r'))):
        # Check if this run contains an image
        has_drawing = r_elem.findall(qn('w:drawing')) or r_elem.findall(
            './/{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}inline'
        )
        if not has_drawing:
            p._element.remove(r_elem)


def insert_paragraph_before(ref_para, text, style=None):
    """Insert a new paragraph element before ref_para and return a Paragraph wrapper."""
    new_p = copy.deepcopy(doc.paragraphs[0]._element)  # template
    # Clear everything
    for child in list(new_p):
        new_p.remove(child)
    # Set style
    pPr = etree.SubElement(new_p, qn('w:pPr'))
    if style:
        pStyle = etree.SubElement(pPr, qn('w:pStyle'))
        pStyle.set(qn('w:val'), style)
    # Add text run
    r = etree.SubElement(new_p, qn('w:r'))
    t = etree.SubElement(r, qn('w:t'))
    t.text = text
    t.set(qn('xml:space'), 'preserve')
    ref_para._element.addprevious(new_p)
    return new_p


def insert_paragraph_after(ref_elem, text, style=None):
    """Insert a new paragraph element after ref_elem (can be a p element)."""
    new_p = etree.SubElement(body, qn('w:p'))  # temporary
    body.remove(new_p)
    # Set style
    pPr = etree.SubElement(new_p, qn('w:pPr'))
    if style:
        pStyle = etree.SubElement(pPr, qn('w:pStyle'))
        pStyle.set(qn('w:val'), style)
    # Add text run
    r = etree.SubElement(new_p, qn('w:r'))
    t = etree.SubElement(r, qn('w:t'))
    t.text = text
    t.set(qn('xml:space'), 'preserve')
    ref_elem.addnext(new_p)
    return new_p


def delete_paragraph(p):
    """Remove a paragraph element from the body."""
    parent = p._element.getparent()
    if parent is not None:
        parent.remove(p._element)


def copy_style_from(source_p, new_p_elem):
    """Copy pPr (paragraph properties) from source paragraph to new element."""
    src_pPr = source_p._element.find(qn('w:pPr'))
    if src_pPr is not None:
        existing = new_p_elem.find(qn('w:pPr'))
        if existing is not None:
            new_p_elem.remove(existing)
        new_p_elem.insert(0, copy.deepcopy(src_pPr))


# ── Reference paragraphs ─────────────────────────────────────────────
P = doc.paragraphs
# Get actual style IDs from existing paragraphs
normal_style = P[18].style.name  # "Normal" - from INTRODUÇÃO body text
heading2_style = P[25].style.name  # "Heading 2"
legenda_style = P[59].style.name  # "Legenda TCC"
ref_style = P[80].style.name  # "Referencia TCC"

print(f"Styles: normal={normal_style}, h2={heading2_style}, legenda={legenda_style}, ref={ref_style}")
print(f"Total paragraphs: {len(P)}")


# ══════════════════════════════════════════════════════════════════════
# 1. P22 – Reescrever objetivo (tirar vermelho) e separar imagem
# ══════════════════════════════════════════════════════════════════════
p22 = P[22]

# Extract the image element from P22 before modifying
img_runs = []
text_runs = []
for r_elem in list(p22._element.findall(qn('w:r'))):
    has_drawing = (
        r_elem.findall(qn('w:drawing'))
        or r_elem.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}inline')
    )
    if has_drawing:
        img_runs.append(r_elem)
    else:
        text_runs.append(r_elem)

# Remove image from P22 (we'll place it properly later)
for r_elem in img_runs:
    p22._element.remove(r_elem)

# Rewrite P22 text
new_obj = (
    "O objetivo geral deste trabalho é aplicar o modelo preditivo MLBatLife para "
    "estimar o estado de saúde (SOH) de baterias em sistemas fotovoltaicos "
    "residenciais, comparando perfis de consumo de diferentes contextos geográficos. "
    "Para alcançar esse propósito, foram construídos perfis de potência residual a "
    "partir de dados reais do projeto Open Power System Data (Alemanha) e de um perfil "
    "sintético representativo do consumo residencial brasileiro, com geração "
    "fotovoltaica estimada pela base PVGIS do Joint Research Centre da Comissão "
    "Europeia. A partir desses perfis, o modelo estima o SOH diário da bateria, "
    "permitindo avaliar como diferentes padrões de consumo e geração influenciam a "
    "degradação ao longo do tempo (LUQUE et al., 2025; AITIO; HOWEY, 2021)."
)
# Clear existing text runs
for r_elem in text_runs:
    p22._element.remove(r_elem)
# Add new text
run = p22.add_run(new_obj)
run.font.color.rgb = RGBColor(0, 0, 0)  # black, not red


# ══════════════════════════════════════════════════════════════════════
# 2. P23 – Remover nota vermelha sobre constrained-off
# ══════════════════════════════════════════════════════════════════════
delete_paragraph(P[23])


# ══════════════════════════════════════════════════════════════════════
# 3. P28-P29 – Substituir por seção sobre curtailment
#    P28 = "Adicionar seção na fundamentação teórica sobre constrained-off"
#    P29 = URL
#    Vamos substituir P28 pelo heading e P29 pelo conteúdo
# ══════════════════════════════════════════════════════════════════════
p28 = P[28]
p29 = P[29]

# Convert P28 to Heading 2
set_paragraph_text(p28, "Curtailment e motivação para o armazenamento de energia")
p28.style = doc.styles[heading2_style]

# Replace P29 with first content paragraph
curtailment_text1 = (
    "O crescimento acelerado da geração solar fotovoltaica no Brasil tem evidenciado "
    "limitações na capacidade de absorção da rede elétrica, resultando em eventos de "
    "curtailment, nos quais a geração disponível é reduzida ou interrompida mesmo com "
    "recurso solar suficiente. No contexto do Sistema Interligado Nacional (SIN), o "
    "Operador Nacional do Sistema Elétrico (ONS) pode determinar o constrained-off de "
    "usinas por razões de segurança operativa, sobrecarga na transmissão ou controle de "
    "tensão, conforme regulamentação da Agência Nacional de Energia Elétrica "
    "(BRASIL, 2021)."
)
set_paragraph_text(p29, curtailment_text1)
p29.style = doc.styles[normal_style]
# Set font color to black
for r in p29.runs:
    r.font.color.rgb = RGBColor(0, 0, 0)

# Insert additional curtailment paragraphs after P29
curtailment_text2 = (
    "Em sistemas residenciais, embora o constrained-off regulatório não se aplique "
    "diretamente, a mesma dinâmica ocorre quando a geração fotovoltaica excede o consumo "
    "instantâneo da residência. Nesses períodos, o excedente é exportado para a rede por "
    "meio de compensação de créditos, porém, com a tendência de redução das tarifas de "
    "compensação e o aumento da penetração fotovoltaica, o armazenamento local por "
    "baterias torna-se uma alternativa relevante para maximizar o autoconsumo e a "
    "viabilidade econômica do sistema (SILVA, 2018; LUQUE et al., 2025)."
)
p_ct2 = insert_paragraph_after(p29._element, curtailment_text2, normal_style)

curtailment_text3 = (
    "Nesse contexto, a bateria assume o papel de deslocar temporalmente a energia "
    "excedente gerada durante o dia para os horários de maior demanda, como o período "
    "noturno. Essa estratégia reduz a dependência da rede e aumenta a fração de "
    "autoconsumo, mas impõe ciclos adicionais de carga e descarga à bateria, acelerando "
    "sua degradação. Portanto, compreender o impacto do perfil de consumo e geração na "
    "saúde da bateria é fundamental para dimensionar adequadamente o sistema de "
    "armazenamento e planejar sua substituição (AITIO; HOWEY, 2021; LUQUE et al., 2025)."
)
p_ct3 = insert_paragraph_after(p_ct2, curtailment_text3, normal_style)

# Now insert the image (from P22) after curtailment section with title and source
# Title paragraph
img_title = insert_paragraph_after(p_ct3,
    "Figura 2 - Perfil diário normalizado de consumo residencial, "
    "geração fotovoltaica e potência excedente",
    legenda_style)

# Image paragraph - create a new paragraph and insert the image runs
img_p = insert_paragraph_after(img_title, "", normal_style)
# Move image elements into this paragraph
for r_elem in img_runs:
    img_p.append(r_elem)

# Source paragraph
img_source = insert_paragraph_after(img_p, "Fonte: Elaborado pelos autores.", legenda_style)


# ══════════════════════════════════════════════════════════════════════
# 4. P51 – Remover duplicata (features T1/T4)
# ══════════════════════════════════════════════════════════════════════
# P51 is a duplicate of P50. Find it by matching text.
# Note: after deletions above, paragraph indices may have shifted.
# We use the original P[] references which still point to the same elements.
delete_paragraph(P[51])


# ══════════════════════════════════════════════════════════════════════
# 5. Atualizar metodologia – adicionar descrição OPSD + Brasil
# ══════════════════════════════════════════════════════════════════════
# P52 currently describes sample CSV data. Update it.
p52 = P[52]
new_p52_text = (
    "Para avaliar o impacto de diferentes perfis de consumo na degradação da bateria, "
    "foram utilizadas duas fontes de dados complementares. A primeira consiste em dados "
    "reais de consumo e geração fotovoltaica de residências alemãs, obtidos do projeto "
    "Open Power System Data (OPSD), que disponibiliza medições de energia em resolução "
    "de um minuto, incluindo importação e exportação da rede e geração fotovoltaica "
    "(OPEN POWER SYSTEM DATA, 2020). Foram selecionadas três residências "
    "(residential3, residential4 e residential6) com períodos de dados completos "
    "variando de 495 a 847 dias."
)
set_paragraph_text(p52, new_p52_text)
for r in p52.runs:
    r.font.color.rgb = RGBColor(0, 0, 0)

# Insert new paragraph about Brazilian profile after P52
brasil_meth = (
    "A segunda fonte consiste em um perfil sintético representativo de uma residência "
    "brasileira na cidade de Vitória-ES, construído a partir da combinação de duas bases: "
    "(i) a curva de carga residencial típica publicada pela pesquisa de posse e hábitos "
    "de uso de equipamentos elétricos (PPH) do Programa Nacional de Conservação de "
    "Energia Elétrica (PROCEL/ELETROBRAS, 2019), que fornece a distribuição horária "
    "normalizada do consumo; e (ii) dados de irradiância solar e geração fotovoltaica "
    "estimados pelo Photovoltaic Geographical Information System (PVGIS) do Joint "
    "Research Centre da Comissão Europeia, utilizando a base de dados ERA5 com resolução "
    "horária para a localidade de Vitória (latitude −20,32°, longitude −40,34°) "
    "(HULD et al., 2012). O perfil foi parametrizado para um consumo mensal de 200 kWh "
    "e um sistema fotovoltaico de 5 kWp, resultando em 1.825 dias de dados."
)
p_brasil = insert_paragraph_after(p52._element, brasil_meth, normal_style)

brasil_conv = (
    "A conversão dos dados para o formato de entrada do MLBatLife foi realizada por "
    "meio de scripts Python desenvolvidos para este trabalho. Para os dados OPSD, a "
    "potência residual foi calculada como a diferença entre a variação de energia "
    "importada e exportada da rede em cada intervalo de um minuto, convertida para "
    "watts. Para o perfil brasileiro, a curva de carga horária foi interpolada para "
    "resolução de um minuto e combinada com a geração fotovoltaica estimada pelo PVGIS, "
    "igualmente interpolada. Em ambos os casos, o formato resultante consiste em um "
    "arquivo CSV com colunas de tempo acumulado (em minutos) e potência residual "
    "(em watts), conforme especificação do MLBatLife (LUQUE et al., 2025)."
)
p_conv = insert_paragraph_after(p_brasil, brasil_conv, normal_style)


# ══════════════════════════════════════════════════════════════════════
# 6. P64 – Remover duplicata (resumo estatístico)
# ══════════════════════════════════════════════════════════════════════
delete_paragraph(P[64])


# ══════════════════════════════════════════════════════════════════════
# 7. Atualizar seção RESULTADOS E DISCUSSÃO
# ══════════════════════════════════════════════════════════════════════
# P62 – intro da seção (ainda em tempo futuro)
p62 = P[62]
new_p62 = (
    "A aplicação do modelo MLBatLife aos quatro perfis de potência residual "
    "permitiu estimar a evolução diária do SOH para cada cenário. Os perfis OPSD "
    "representam condições reais de residências alemãs com diferentes padrões de "
    "consumo e capacidade fotovoltaica, enquanto o perfil brasileiro simula uma "
    "residência típica em Vitória-ES com sistema de 5 kWp. Todos os cenários "
    "utilizaram estratégia Greedy (SOH₀ = 1,0, Qnom = 5 kWh), que prioriza o "
    "autoconsumo imediato sem limitar a profundidade de descarga "
    "(LUQUE et al., 2025)."
)
set_paragraph_text(p62, new_p62)
for r in p62.runs:
    r.font.color.rgb = RGBColor(0, 0, 0)

# P63 – resumo estatístico → substituir por tabela comparativa em texto
p63 = P[63]
new_p63 = (
    "A Tabela 2 apresenta os resultados consolidados da estimativa de SOH para os "
    "quatro perfis analisados. O perfil brasileiro (Vitória-ES) apresentou a maior "
    "degradação, com SOH final de 0,8055 após 1.825 dias (5 anos), enquanto os perfis "
    "alemães, com períodos de observação menores (495 a 847 dias), mantiveram o SOH "
    "acima de 0,89. Essa diferença decorre tanto da maior duração do perfil brasileiro "
    "quanto do balanço energético negativo (T1 médio de −616,6 W), indicando que a "
    "geração fotovoltaica supera consistentemente o consumo, resultando em ciclos "
    "diários mais intensos de carga e descarga da bateria "
    "(LUQUE et al., 2025; AITIO; HOWEY, 2021)."
)
set_paragraph_text(p63, new_p63)
for r in p63.runs:
    r.font.color.rgb = RGBColor(0, 0, 0)

# P65 – avaliação modelos regressão → resultados features
p65 = P[65]
new_p65 = (
    "A análise das features extraídas pelo MLBatLife revelou diferenças significativas "
    "entre os perfis. A feature T1 (média diária da potência residual) apresentou "
    "valores negativos para os perfis com maior capacidade fotovoltaica relativa ao "
    "consumo (residential4: −434,9 W; Brasil: −616,6 W), indicando exportação líquida "
    "de energia. Em contrapartida, perfis com menor geração relativa "
    "(residential3: 21,6 W; residential6: 48,4 W) apresentaram T1 positivo, "
    "caracterizando importação líquida. A feature T4 (média do valor absoluto da "
    "potência) reflete a intensidade total do fluxo de energia, sendo mais elevada nos "
    "perfis com maior variabilidade (residential4: 1.421,7 W; Brasil: 931,8 W) "
    "(LUQUE et al., 2025)."
)
set_paragraph_text(p65, new_p65)
for r in p65.runs:
    r.font.color.rgb = RGBColor(0, 0, 0)

# P66 – avaliação modelos classificação → discussão SOH
p66 = P[66]
new_p66 = (
    "Observou-se que a taxa de degradação não é uniforme ao longo do tempo. Nos "
    "primeiros meses de operação, a queda de SOH é mais acentuada, tendendo a "
    "desacelerar à medida que a bateria envelhece. Esse comportamento, consistente com "
    "a literatura sobre envelhecimento de baterias de íon-lítio, sugere que os primeiros "
    "ciclos impõem maior estresse eletroquímico devido à formação da camada de interface "
    "sólido-eletrólito (SEI). A projeção do perfil brasileiro indica que a bateria "
    "atingiria o limiar de fim de vida útil (SOH = 0,80) em aproximadamente 5,2 anos, "
    "informação relevante para o planejamento de substituição e para a análise de "
    "viabilidade econômica do sistema de armazenamento "
    "(AITIO; HOWEY, 2021; LUQUE et al., 2025)."
)
set_paragraph_text(p66, new_p66)
for r in p66.runs:
    r.font.color.rgb = RGBColor(0, 0, 0)

# P74 – discussão final → atualizar
p74 = P[74]
new_p74 = (
    "A comparação entre os perfis evidenciou que o padrão de consumo residencial e a "
    "capacidade do sistema fotovoltaico exercem influência direta sobre a degradação "
    "da bateria. Perfis com maior geração fotovoltaica relativa ao consumo tendem a "
    "produzir ciclos de carga e descarga mais profundos, acelerando a perda de "
    "capacidade. Essa constatação é coerente com os resultados de Aitio e Howey (2021), "
    "que identificaram o perfil de uso como fator determinante na previsão do fim de "
    "vida útil de baterias em sistemas off-grid. A diferença entre os perfis alemães e o "
    "perfil brasileiro também reflete a influência da irradiância solar local, uma vez "
    "que a maior disponibilidade de recurso solar em Vitória-ES resulta em maior geração "
    "fotovoltaica e, consequentemente, maior ciclagem da bateria "
    "(PEREIRA et al., 2017; LUQUE et al., 2025)."
)
set_paragraph_text(p74, new_p74)
for r in p74.runs:
    r.font.color.rgb = RGBColor(0, 0, 0)


# ══════════════════════════════════════════════════════════════════════
# 8. Adicionar tabela comparativa após P63
# ══════════════════════════════════════════════════════════════════════
# Find P63 element and insert table title + table + source after it
p63_elem = P[63]._element

# Table title
tbl_title = insert_paragraph_after(p63_elem,
    "Tabela 2 - Resultados consolidados da estimativa de SOH por perfil",
    legenda_style)

# Create actual table
from docx.shared import Cm
table = doc.add_table(rows=5, cols=5)
table.style = 'Table Grid'
# Header
headers = ['Perfil', 'Dias', 'SOH final', 'T1 médio (W)', 'T4 médio (W)']
for i, h in enumerate(headers):
    table.rows[0].cells[i].text = h
# Data
data = [
    ['OPSD residential3', '495', '0,9279', '21,6', '803,4'],
    ['OPSD residential4', '847', '0,8956', '−434,9', '1.421,7'],
    ['OPSD residential6', '694', '0,9216', '48,4', '454,7'],
    ['Brasil (Vitória-ES)', '1.825', '0,8055', '−616,6', '931,8'],
]
for row_idx, row_data in enumerate(data, 1):
    for col_idx, val in enumerate(row_data):
        table.rows[row_idx].cells[col_idx].text = val

# Move table after the title paragraph
tbl_elem = table._tbl
body.remove(tbl_elem)
tbl_title.addnext(tbl_elem)

# Table source
tbl_source = insert_paragraph_after(tbl_elem,
    "Fonte: Elaborado pelos autores com dados do MLBatLife.",
    legenda_style)


# ══════════════════════════════════════════════════════════════════════
# 9. Atualizar REFERÊNCIAS
# ══════════════════════════════════════════════════════════════════════
# Find last reference paragraph
last_ref = P[86]  # SILVA reference

new_refs = [
    (
        "BRASIL. Agência Nacional de Energia Elétrica. Resolução Normativa nº 927, "
        "de 14 de dezembro de 2021. Estabelece regras para o constrained-off de "
        "centrais geradoras. Diário Oficial da União, Brasília, 2021."
    ),
    (
        "EMPRESA DE PESQUISA ENERGÉTICA. Anuário estatístico de energia elétrica "
        "2023: ano base 2022. Rio de Janeiro: EPE, 2023."
    ),
    (
        "HULD, Thomas et al. A new solar radiation database for estimating PV "
        "performance in Europe and Africa. Solar Energy, v. 86, n. 6, "
        "p. 1803-1815, 2012."
    ),
    (
        "OPEN POWER SYSTEM DATA. Data package household data. Version 2020-04-15. "
        "Disponível em: https://data.open-power-system-data.org/household_data/2020-04-15/. "
        "Acesso em: jun. 2025."
    ),
    (
        "PEREIRA, Enio Bueno et al. Atlas brasileiro de energia solar. 2. ed. "
        "São José dos Campos: INPE, 2017."
    ),
    (
        "PROCEL/ELETROBRAS. Pesquisa de posse e hábitos de uso de equipamentos "
        "elétricos na classe residencial: relatório Brasil 2019. "
        "Rio de Janeiro: Eletrobras, 2019."
    ),
    (
        "RUSSELL, Stuart; NORVIG, Peter. Artificial intelligence: a modern "
        "approach. 4. ed. Hoboken: Pearson, 2020."
    ),
]

# Collect ALL references (existing + new) and sort alphabetically
existing_refs = []
for idx in range(80, 87):
    if idx < len(P):
        txt = P[idx].text.strip()
        if txt:
            existing_refs.append(txt)

all_refs = existing_refs + new_refs
# Sort by first author surname (text before first comma or period)
all_refs_sorted = sorted(set(all_refs), key=lambda x: x.upper())

# Remove old reference paragraphs (P80-P86)
for idx in range(86, 79, -1):
    if idx < len(P):
        delete_paragraph(P[idx])

# Insert new sorted references after the REFERÊNCIAS heading (P79)
p79_elem = P[79]._element
prev = p79_elem
for ref_text in all_refs_sorted:
    new_ref = insert_paragraph_after(prev, ref_text, ref_style)
    prev = new_ref


# ══════════════════════════════════════════════════════════════════════
# 10. Renumerar figuras: image1 agora é Figura 2 (na fund. teórica)
#     Figura original "Figura 1 - Perfil de potência residual" mantém
#     "Gráfico 1" → "Gráfico 1" (mantém)
#     "Figura 2 - Matriz de correlação" → "Figura 3"
# ══════════════════════════════════════════════════════════════════════
# P59 currently: "Figura 1 - Perfil de potência residual (primeiro dia)"
# Keep as is (still Figura 1 in METODOLOGIA)

# P71: "Figura 2 - Matriz de correlação das variáveis" → "Figura 3"
p71 = P[71]
if "Figura 2" in p71.text:
    set_paragraph_text(p71, "Figura 3 - Matriz de correlação das variáveis")


# ══════════════════════════════════════════════════════════════════════
# 11. Atualizar CONSIDERAÇÕES FINAIS (P76-78)
# ══════════════════════════════════════════════════════════════════════
p76 = P[76]
new_p76 = (
    "Este trabalho aplicou o modelo preditivo MLBatLife para estimar o estado de saúde "
    "de baterias em sistemas fotovoltaicos residenciais, comparando perfis de consumo "
    "de residências alemãs (dados OPSD) e de um cenário sintético brasileiro "
    "(Vitória-ES). Os resultados demonstraram que o padrão de consumo e a capacidade "
    "fotovoltaica instalada influenciam diretamente a taxa de degradação da bateria, "
    "com o perfil brasileiro apresentando SOH final de 0,8055 após cinco anos de "
    "operação simulada, próximo ao limiar convencional de fim de vida útil "
    "(LUQUE et al., 2025; AITIO; HOWEY, 2021)."
)
set_paragraph_text(p76, new_p76)
for r in p76.runs:
    r.font.color.rgb = RGBColor(0, 0, 0)

p77 = P[77]
new_p77 = (
    "Como limitação, destaca-se que o perfil brasileiro foi construído a partir de "
    "dados sintéticos, combinando a curva de carga PROCEL com geração estimada pelo "
    "PVGIS, o que pode não representar integralmente a variabilidade real do consumo "
    "residencial. Além disso, o modelo MLBatLife considera apenas a estratégia Greedy "
    "de operação, não contemplando estratégias otimizadas de carga e descarga que "
    "poderiam prolongar a vida útil da bateria. A validação com dados de campo de "
    "sistemas brasileiros é recomendada para futuros trabalhos "
    "(AITIO; HOWEY, 2021; PEDREGOSA et al., 2011)."
)
set_paragraph_text(p77, new_p77)
for r in p77.runs:
    r.font.color.rgb = RGBColor(0, 0, 0)


# ══════════════════════════════════════════════════════════════════════
# SALVAR
# ══════════════════════════════════════════════════════════════════════
OLD.mkdir(exist_ok=True)
doc.save(str(DST))
print(f"\nSalvo: {DST}")

# Mover v4 para _old/
old_dst = OLD / SRC.name
if not old_dst.exists():
    shutil.copy2(str(SRC), str(old_dst))
    print(f"Backup: {old_dst}")
else:
    print(f"Backup já existe: {old_dst}")

print("\nConcluído! Revise o documento v5.")
