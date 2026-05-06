#!/usr/bin/env python3
"""
Ajuste por mínimos quadrados do sensor LM35.
Usa a biblioteca minimos_quadrados para ajustar retas a V_out e V_out condicionado.
Plota os pontos experimentais com as retas ajustadas.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from minimos_quadrados import minimos_quadrados, avaliar, residuos, formatar_equacao

CSV_PATH = "data/LM35/lab.csv"
OUT_DIR = "data/LM35"


def load_data():
    df = pd.read_csv(CSV_PATH, skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]
    return df


def main():
    df = load_data()
    temp = df.iloc[:, 0].values
    vout = df.iloc[:, 1].values
    vout_cond = df.iloc[:, 2].values

    # --- Ajuste por mínimos quadrados (grau 1 = reta) ---
    coefs_vout = minimos_quadrados(temp, vout, grau=1)
    coefs_cond = minimos_quadrados(temp, vout_cond, grau=1)

    # métricas
    stats_vout = residuos(coefs_vout, temp, vout)
    stats_cond = residuos(coefs_cond, temp, vout_cond)

    eq_vout = formatar_equacao(coefs_vout, var="T")
    eq_cond = formatar_equacao(coefs_cond, var="T")

    print("=" * 60)
    print("📐 AJUSTE POR MÍNIMOS QUADRADOS — LM35")
    print("=" * 60)
    print(f"\nV_out:")
    print(f"  {eq_vout}")
    print(f"  a = {coefs_vout[0]:.4f} mV/°C,  b = {coefs_vout[1]:.4f} mV")
    print(f"  R² = {stats_vout['R2']:.6f}")
    print(f"\nV_out condicionado:")
    print(f"  {eq_cond}")
    print(f"  a = {coefs_cond[0]:.4f} mV/°C,  b = {coefs_cond[1]:.4f} mV")
    print(f"  R² = {stats_cond['R2']:.6f}")

    # --- Pontos da reta para plotar ---
    t_fit = np.linspace(temp.min() - 2, temp.max() + 2, 200)
    y_fit_vout = avaliar(coefs_vout, t_fit)
    y_fit_cond = avaliar(coefs_cond, t_fit)

    # --- Plot ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # V_out
    ax1.scatter(temp, vout, color="#4472C4", s=50, edgecolors="black",
                linewidths=0.5, zorder=3, label="Dados experimentais")
    ax1.plot(t_fit, y_fit_vout, "r-", linewidth=1.5, zorder=2,
             label=f"MMQ: {eq_vout}\nR² = {stats_vout['R2']:.6f}")
    ax1.set_xlabel("Temperatura (°C)", fontsize=12)
    ax1.set_ylabel("V_out (mV)", fontsize=12)
    ax1.set_title("V_out × Temperatura", fontsize=13, fontweight="bold")
    ax1.legend(fontsize=9, loc="upper left")
    ax1.grid(True, alpha=0.3)

    # V_out condicionado
    ax2.scatter(temp, vout_cond, color="#ED7D31", s=50, edgecolors="black",
                linewidths=0.5, zorder=3, label="Dados experimentais")
    ax2.plot(t_fit, y_fit_cond, "r-", linewidth=1.5, zorder=2,
             label=f"MMQ: {eq_cond}\nR² = {stats_cond['R2']:.6f}")
    ax2.set_xlabel("Temperatura (°C)", fontsize=12)
    ax2.set_ylabel("V_out condicionado (mV)", fontsize=12)
    ax2.set_title("V_out Condicionado × Temperatura", fontsize=13, fontweight="bold")
    ax2.legend(fontsize=9, loc="upper left")
    ax2.grid(True, alpha=0.3)

    fig.suptitle("Sensor LM35 — Ajuste por Mínimos Quadrados", fontsize=15, fontweight="bold")
    plt.tight_layout()

    out_path = os.path.join(OUT_DIR, "ajuste_mmq_lm35.png")
    plt.savefig(out_path, dpi=150)
    print(f"\n📊 Gráfico salvo em: {out_path}")
    plt.close()


if __name__ == "__main__":
    main()
