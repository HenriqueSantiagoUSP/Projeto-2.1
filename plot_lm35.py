#!/usr/bin/env python3
"""Gera tabela em PNG e gráficos de dispersão do sensor LM35."""

import pandas as pd
import matplotlib.pyplot as plt
import os

CSV_PATH = "data/LM35/lab.csv"
OUT_DIR = "data/LM35"


def load_data():
    df = pd.read_csv(CSV_PATH, skipinitialspace=True)
    # limpar nomes de colunas
    df.columns = [c.strip() for c in df.columns]
    return df


def plot_table(df):
    """Renderiza a tabela de dados como imagem PNG."""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis("off")
    ax.set_title("Ensaio LM35 — Dados do Laboratório", fontsize=14,
                 fontweight="bold", pad=20)

    col_labels = ["Temperatura (°C)", "V_out (mV)", "V_out cond. (mV)"]
    cell_text = [[f"{row[0]:.1f}", f"{row[1]:.2f}", f"{row[2]:.1f}"]
                 for row in df.values]

    table = ax.table(
        cellText=cell_text,
        colLabels=col_labels,
        cellLoc="center",
        loc="center",
    )

    # estilo
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.0, 1.4)

    # header com cor
    for j in range(len(col_labels)):
        table[0, j].set_facecolor("#4472C4")
        table[0, j].set_text_props(color="white", fontweight="bold")

    # linhas alternadas
    for i in range(1, len(cell_text) + 1):
        color = "#D6E4F0" if i % 2 == 0 else "white"
        for j in range(len(col_labels)):
            table[i, j].set_facecolor(color)

    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, "tabela_lm35.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"✅ Tabela salva em: {out_path}")
    plt.close()


def plot_scatter(df):
    """Plota V_out e V_out condicionado em função da temperatura."""
    temp = df.iloc[:, 0]
    vout = df.iloc[:, 1]
    vout_cond = df.iloc[:, 2]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # --- V_out vs Temperatura ---
    ax1.scatter(temp, vout, color="#4472C4", s=50, edgecolors="black", linewidths=0.5, zorder=3)
    ax1.set_xlabel("Temperatura (°C)", fontsize=12)
    ax1.set_ylabel("V_out (mV)", fontsize=12)
    ax1.set_title("V_out × Temperatura", fontsize=13, fontweight="bold")
    ax1.grid(True, alpha=0.3)

    # --- V_out condicionado vs Temperatura ---
    ax2.scatter(temp, vout_cond, color="#ED7D31", s=50, edgecolors="black", linewidths=0.5, zorder=3)
    ax2.set_xlabel("Temperatura (°C)", fontsize=12)
    ax2.set_ylabel("V_out condicionado (mV)", fontsize=12)
    ax2.set_title("V_out Condicionado × Temperatura", fontsize=13, fontweight="bold")
    ax2.grid(True, alpha=0.3)

    fig.suptitle("Sensor LM35 — Caracterização", fontsize=15, fontweight="bold")
    plt.tight_layout()

    out_path = os.path.join(OUT_DIR, "graficos_lm35.png")
    plt.savefig(out_path, dpi=150)
    print(f"✅ Gráficos salvos em: {out_path}")
    plt.close()


def main():
    df = load_data()
    print(f"📁 {len(df)} medições carregadas de {CSV_PATH}")
    print(df.to_string(index=False))
    print()

    plot_table(df)
    plot_scatter(df)


if __name__ == "__main__":
    main()
