# Modelo Preditivo para Estimativa do SOH e EOL de Baterias em Sistemas Fotovoltaicos

> **Predictive Model for Estimating Battery State of Health and End of Life in Photovoltaic Systems**

Trabalho de Conclusão de Curso (TCC) — Ciência da Computação / Sistemas de Informação  
Centro Universitário Espírito-santense — FAESA 
Autores: Nicolas Lima Rosário · Vitor Dornela Mascarenhas  
Orientador: Prof. Dr. Wesley Pereira da Silva

---

## Resumo

Este trabalho propõe o uso do projeto [MLBatLife](https://github.com/joaquinluque/MLBatLife) como base para um modelo preditivo capaz de estimar o **estado de saúde (SOH)** e o **fim da vida útil (EOL)** de baterias aplicadas a sistemas fotovoltaicos. A partir de perfis de potência residual (demanda menos geração) e de um modelo Random Forest pré-treinado, são extraídas *features* diárias e estimado o SOH ao longo do tempo. Limiares operacionais (≥ 0,90 "Saudável"; 0,80–0,90 "Atenção"; < 0,80 "Fim de vida"), métricas de regressão e gráficos de análise apoiam a manutenção preditiva e a redução de falhas inesperadas.

## Estrutura do Repositório

```
├── code/
│   ├── data/                # Dados de entrada e figuras geradas
│   │   ├── brasil/          # Perfil de geração/consumo de Vitória-ES
│   │   ├── opsd/            # Perfis europeus (OPSD household)
│   │   └── pic/             # Figuras exportadas pelos notebooks
│   ├── model/               # MLBatLife — modelo RF pré-treinado (.pkl) e scripts
│   ├── notebooks/           # Notebooks de análise (Jupyter)
│   └── requirements.txt     # Dependências Python
├── doc/                     # Artigo (docx e pdf) 
└── README.md
```

## Pré-requisitos

| Requisito | Versão testada |
|-----------|---------------|
| Python    | 3.12          |
| pip       | ≥ 23          |
| Git LFS   | qualquer (o `.pkl` tem ~886 MB) |

## Como Reproduzir

### 1. Clonar o repositório

```bash
git clone https://github.com/vitor-dornela/Trabalho-de-Conclusao-de-Curso.git
cd Trabalho-de-Conclusao-de-Curso
```

> **Nota:** o arquivo `MLBatLife_Model.pkl` (~886 MB) é rastreado via Git LFS.  
> Se o clone não baixá-lo automaticamente, execute `git lfs pull`.

### 2. Criar e ativar o ambiente virtual

```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r code/requirements.txt
```

> **Importante:** `scikit-learn==1.4.0` está fixado para garantir compatibilidade com o modelo `.pkl`.

### 4. Obter os dados de entrada

| Dataset | Origem | Local esperado |
|---------|--------|----------------|
| OPSD Household | [open-power-system-data.org](https://data.open-power-system-data.org/household_data/) | `code/data/opsd/household_data_1min_singleindex.csv` |
| Perfil Brasil (Vitória-ES) | INMET / EPE (baixado automaticamente pelo notebook) | `code/data/brasil/` |

### 5. Executar os notebooks

Abrir no VS Code (ou Jupyter) e executar **na ordem**:

1. **`Notebook_Perfis_OPSD.ipynb`** — Processa os perfis europeus via MLBatLife e gera curvas de SOH.
2. **`Notebook_Perfil_Brasil.ipynb`** — Processa o perfil brasileiro (Vitória-ES) via MLBatLife.
3. **`Notebook_Resultados_Combinados.ipynb`** — Consolida resultados, gera gráficos comparativos, análise de *feature importance*, extrapolação de EOL e tabela-resumo.

As figuras são salvas automaticamente em `code/data/pic/`.

## Principais Resultados

- **Feature importance (RF):** Dia de operação (61,5 %), SOH₀ (23,7 %), Temperatura T1 (10,8 %), T4 (2,1 %), Estratégia (1,8 %).
- **Classificação de saúde:** perfis com estratégia *Greedy* (descarga profunda) degradam mais rápido, atingindo EOL < 80 % em menos anos.
- **Extrapolação EOL:** regressão linear sobre a curva de SOH (excluindo período de *break-in*) projeta o ano em que cada perfil cruza o limiar de 80 %.

## Tecnologias

- **Python 3.12** · NumPy · Pandas · Matplotlib · scikit-learn 1.4.0
- **MLBatLife** (Luque *et al.*, 2025) — Random Forest com 50 estimadores, `max_depth=30`

## Referências Principais

- LUQUE, A. *et al.* MLBatLife: a machine learning-based battery life predictor for photovoltaic self-consumption applications. *Solar Energy*, 2025.
- AITIO, A.; HOWEY, D. A. Predicting battery end of life from solar off-grid system field data. *Joule*, v. 5, n. 12, 2021.
- BREIMAN, L. Random Forests. *Machine Learning*, v. 45, n. 1, 2001.

## Licença

O modelo MLBatLife (pasta `code/model/`) possui licença própria — consulte `code/model/LICENSE`.  
O restante do repositório é de uso acadêmico.
