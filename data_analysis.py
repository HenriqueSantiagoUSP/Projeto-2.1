#!/usr/bin/env python3
"""
Script de análise dos dados do MPU6050.

Uso:
    python3 data_analysis.py                           # usa o CSV mais recente em data/
    python3 data_analysis.py data/meu_teste.csv        # especifica o arquivo
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import glob


def find_latest_csv():
    """Encontra o CSV mais recente em data/."""
    csvs = glob.glob("data/*.csv")
    if not csvs:
        print("❌ Nenhum CSV encontrado em data/")
        sys.exit(1)
    latest = max(csvs, key=os.path.getmtime)
    return latest


def load_and_process(filepath):
    """Carrega o CSV e adiciona colunas derivadas."""
    print(f"📁 Carregando: {filepath}")

    col_names = ["timestamp_ms", "ax", "ay", "az", "gx", "gy", "gz"]

    # detecta se o CSV já tem header ou não
    with open(filepath, "r") as f:
        first_line = f.readline().strip()

    if first_line.startswith("timestamp_ms"):
        df = pd.read_csv(filepath)
    else:
        df = pd.read_csv(filepath, header=None, names=col_names)

    print(f"   {len(df)} amostras lidas")
    print(f"   Colunas: {list(df.columns)}")

    # tempo relativo (t=0 na primeira medição), convertido para segundos
    df["tempo_s"] = (df["timestamp_ms"] - df["timestamp_ms"].iloc[0]) / 1000.0

    # aceleração resultante: sqrt(ax² + ay² + az²)
    df["a_res"] = np.sqrt(df["ax"]**2 + df["ay"]**2 + df["az"]**2)

    # salvar CSV processado no mesmo diretório do arquivo de entrada
    parent_dir = os.path.dirname(filepath)
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    processed_path = os.path.join(parent_dir, f"{base_name}_processado.csv")
    df.to_csv(processed_path, index=False)
    print(f"💾 CSV processado salvo em: {processed_path}")

    return df


def plot_data(df, filepath):
    """Plota acelerações lineares, rotacionais e resultante."""
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    t = df["tempo_s"]

    # --- Acelerações lineares ---
    ax1 = axes[0]
    ax1.plot(t, df["ax"], label="ax", linewidth=0.8)
    ax1.plot(t, df["ay"], label="ay", linewidth=0.8)
    ax1.plot(t, df["az"], label="az", linewidth=0.8)
    ax1.plot(t, df["a_res"], label="resultante", linewidth=0.8, linestyle="--", color="black")
    ax1.set_ylabel("Aceleração (g)")
    ax1.set_title("Acelerações Lineares")
    ax1.legend(loc="upper right")
    ax1.grid(True, alpha=0.3)

    # --- Velocidades angulares ---
    ax2 = axes[1]
    ax2.plot(t, df["gx"], label="gx", linewidth=0.8)
    ax2.plot(t, df["gy"], label="gy", linewidth=0.8)
    ax2.plot(t, df["gz"], label="gz", linewidth=0.8)
    ax2.set_ylabel("Velocidade Angular (°/s)")
    ax2.set_title("Giroscópio")
    ax2.legend(loc="upper right")
    ax2.grid(True, alpha=0.3)

    # --- Resultante isolada ---
    ax3 = axes[2]
    ax3.plot(t, df["a_res"], label="resultante", linewidth=0.8, color="black")
    ax3.axhline(y=1.0, color="red", linestyle=":", alpha=0.5, label="1g (referência)")
    ax3.set_ylabel("Aceleração (g)")
    ax3.set_xlabel("Tempo (s)")
    ax3.set_title("Aceleração Resultante")
    ax3.legend(loc="upper right")
    ax3.grid(True, alpha=0.3)

    fig.suptitle(f"Caracterização MPU6050 — {os.path.basename(filepath)}", fontsize=14, fontweight="bold")
    plt.tight_layout()

    # salvar figura no mesmo diretório do arquivo de entrada
    parent_dir = os.path.dirname(filepath)
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    fig_path = os.path.join(parent_dir, f"{base_name}_plot.png")
    plt.savefig(fig_path, dpi=150)
    print(f"📊 Gráfico salvo em: {fig_path}")

    plt.show()


def main():
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = find_latest_csv()

    df = load_and_process(filepath)

    # resumo estatístico
    print("\n📈 Resumo estatístico:")
    print(df[["ax", "ay", "az", "a_res", "gx", "gy", "gz"]].describe().round(4).to_string())

    plot_data(df, filepath)


if __name__ == "__main__":
    main()
