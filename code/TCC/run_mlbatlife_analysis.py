# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sys
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE_DIR  = Path(r"c:\Users\vdmas\OneDrive\FAESA\Trabalho de Conclusao de Curso")
MLBAT_DIR = BASE_DIR / "code" / "MLBatLife"
if str(MLBAT_DIR) not in sys.path:
    sys.path.insert(0, str(MLBAT_DIR))

import MLBatLife_Pred as blp

DATA_PATH = BASE_DIR / "code" / "data" / "input_profile_sample.csv"
OUT_DIR   = BASE_DIR / "pic"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# O MLBatLife_Pred carrega o modelo pelo nome relativo; precisa estar no diretório
os.chdir(MLBAT_DIR)

# Parâmetros
strategy = 0  # 0: Greedy, 1: FeedInDamp
Qnom = 5      # kWh

# Carga e processamento
m_time, input_prof = blp.read_csv(str(DATA_PATH))
features, day = blp.extract_features(m_time, input_prof)
soh_hat = blp.estimate_soh(features, day, strategy, Qnom)

# Salva SOH diário
out_table = pd.DataFrame({"day": day, "soh_hat": soh_hat})
out_table.to_csv(OUT_DIR / "soh_daily.csv", index=False)

# Resumo estatístico
summary = pd.DataFrame({
    "metric": ["min", "max", "mean", "std", "final"],
    "value": [
        float(np.min(soh_hat)),
        float(np.max(soh_hat)),
        float(np.mean(soh_hat)),
        float(np.std(soh_hat)),
        float(soh_hat[-1]),
    ],
})
summary.to_csv(OUT_DIR / "soh_summary.csv", index=False)

# Figura 1: SOH ao longo do tempo
plt.figure(figsize=(7.0, 4.0))
plt.plot(day, soh_hat, color="#1f77b4")
plt.xlabel("Dia")
plt.ylabel("SOH")
plt.title("SOH ao longo do tempo")
plt.tight_layout()
plt.savefig(OUT_DIR / "soh_over_time.png", dpi=300)
plt.close()

# Figura 2: Distribuição do SOH
plt.figure(figsize=(6.5, 4.0))
plt.hist(soh_hat, bins=30, color="#2ca02c", alpha=0.85)
plt.xlabel("SOH")
plt.ylabel("Frequência")
plt.title("Distribuição do SOH estimado")
plt.tight_layout()
plt.savefig(OUT_DIR / "soh_distribution.png", dpi=300)
plt.close()

# Figura 3: Correlação entre features (T1, T4, Dia)
features_df = pd.DataFrame({
    "T1 (média)":    features[:, 0],
    "T4 (média abs.)": features[:, 1],
    "Dia":           day,
})
corr = features_df.corr(numeric_only=True)
plt.figure(figsize=(5.8, 4.8))
plt.imshow(corr.values, cmap="viridis", vmin=-1, vmax=1)
plt.colorbar(label="Correlação")
plt.xticks(range(len(corr.columns)), corr.columns, rotation=45, ha="right")
plt.yticks(range(len(corr.columns)), corr.columns)
plt.title("Matriz de correlação das variáveis")
plt.tight_layout()
plt.savefig(OUT_DIR / "feature_correlation.png", dpi=300)
plt.close()

# Figura 4: Importância das features (Random Forest)
with open(MLBAT_DIR / "MLBatLife_Model.pkl", "rb") as f:
    model, mu, sigma, qtr = pickle.load(f)

feature_names = ["SOH0", "T1", "Estratégia", "T4", "Dia"]
importances = getattr(model, "feature_importances_", None)

if importances is not None:
    order = np.argsort(importances)[::-1]
    plt.figure(figsize=(6.8, 4.0))
    plt.bar([feature_names[i] for i in order], importances[order], color="#ff7f0e")
    plt.ylabel("Importância")
    plt.title("Importância das variáveis (Random Forest)")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "feature_importance.png", dpi=300)
    plt.close()

# Figura 5: Perfil de potência residual (primeiro dia)
minutes_per_day = 24 * 60
first_day_profile = input_prof[:minutes_per_day]
plt.figure(figsize=(7.0, 4.0))
plt.plot(np.arange(minutes_per_day), first_day_profile, color="#9467bd")
plt.xlabel("Minuto do dia")
plt.ylabel("Potência (W)")
plt.title("Perfil de potência residual (primeiro dia)")
plt.tight_layout()
plt.savefig(OUT_DIR / "input_profile_first_day.png", dpi=300)
plt.close()

print("Outputs salvos em", OUT_DIR)
