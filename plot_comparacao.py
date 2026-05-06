#!/usr/bin/env python3
"""Gera gráfico comparativo das 5 classes de ensaio (sem adivinhe)."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

DATA_DIR = "data"
COL_NAMES = ["timestamp_ms", "ax", "ay", "az", "gx", "gy", "gz"]

CLASSES = ["andando", "correndo", "caindo_frente", "caindo_joelho", "caindo_costas"]
TITLES = ["Andando", "Correndo", "Caindo (frente)", "Caindo (joelho)", "Caindo (costas)"]


def load_csv(filepath):
    with open(filepath, "r") as f:
        first_line = f.readline().strip()
    if first_line.startswith("timestamp_ms"):
        df = pd.read_csv(filepath)
    else:
        df = pd.read_csv(filepath, header=None, names=COL_NAMES)
    df["tempo_s"] = (df["timestamp_ms"] - df["timestamp_ms"].iloc[0]) / 1000.0
    df["a_res"] = np.sqrt(df["ax"]**2 + df["ay"]**2 + df["az"]**2)
    return df


def main():
    fig, axes = plt.subplots(3, 5, figsize=(22, 10))

    for col, (cls, title) in enumerate(zip(CLASSES, TITLES)):
        # carregar o ensaio _1 como representante
        csv_path = os.path.join(DATA_DIR, f"{cls}_1", f"{cls}_1.csv")
        if not os.path.exists(csv_path):
            print(f"⚠️  {csv_path} não encontrado, pulando.")
            continue

        df = load_csv(csv_path)
        t = df["tempo_s"]

        # --- Linha 1: Aceleração resultante ---
        ax1 = axes[0, col]
        ax1.plot(t, df["a_res"], "k-", linewidth=0.6)
        ax1.axhline(y=1.0, color="red", linestyle=":", alpha=0.4)
        ax1.set_title(title, fontsize=12, fontweight="bold")
        ax1.set_ylim(0, max(df["a_res"].max() * 1.15, 2.5))
        ax1.grid(True, alpha=0.2)
        if col == 0:
            ax1.set_ylabel("a_res (g)", fontsize=10)

        # --- Linha 2: Acelerações ax, ay, az ---
        ax2 = axes[1, col]
        ax2.plot(t, df["ax"], linewidth=0.6, label="ax")
        ax2.plot(t, df["ay"], linewidth=0.6, label="ay")
        ax2.plot(t, df["az"], linewidth=0.6, label="az")
        ax2.grid(True, alpha=0.2)
        if col == 0:
            ax2.set_ylabel("Aceleração (g)", fontsize=10)
            ax2.legend(fontsize=8, loc="upper left")

        # --- Linha 3: Magnitude do giroscópio ---
        ax3 = axes[2, col]
        g_mag = np.sqrt(df["gx"]**2 + df["gy"]**2 + df["gz"]**2)
        ax3.plot(t, g_mag, "m-", linewidth=0.6)
        ax3.grid(True, alpha=0.2)
        ax3.set_xlabel("Tempo (s)", fontsize=10)
        if col == 0:
            ax3.set_ylabel("Gyro mag (°/s)", fontsize=10)

    fig.suptitle("Comparação dos Ensaios — Acelerômetro MPU6050",
                 fontsize=15, fontweight="bold")
    plt.tight_layout()

    out_path = os.path.join(DATA_DIR, "comparacao_ensaios.png")
    plt.savefig(out_path, dpi=150)
    print(f"✅ Gráfico salvo em: {out_path}")


if __name__ == "__main__":
    main()
