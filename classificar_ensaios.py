#!/usr/bin/env python3
"""
Análise comparativa dos ensaios do MPU6050.
Identifica padrões nos ensaios conhecidos e classifica os ensaios misteriosos.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob


DATA_DIR = "data"
COL_NAMES = ["timestamp_ms", "ax", "ay", "az", "gx", "gy", "gz"]


def load_csv(filepath):
    """Carrega um CSV com ou sem header."""
    with open(filepath, "r") as f:
        first_line = f.readline().strip()

    if first_line.startswith("timestamp_ms"):
        df = pd.read_csv(filepath)
    else:
        df = pd.read_csv(filepath, header=None, names=COL_NAMES)

    df["tempo_s"] = (df["timestamp_ms"] - df["timestamp_ms"].iloc[0]) / 1000.0
    df["a_res"] = np.sqrt(df["ax"]**2 + df["ay"]**2 + df["az"]**2)
    return df


def extract_features(df):
    """Extrai features estatísticas de um ensaio."""
    a_res = df["a_res"]
    ax, ay, az = df["ax"], df["ay"], df["az"]
    gx, gy, gz = df["gx"], df["gy"], df["gz"]

    # duração
    duration = df["tempo_s"].iloc[-1] - df["tempo_s"].iloc[0]

    # features da aceleração resultante
    features = {
        # --- Aceleração resultante ---
        "a_res_mean": a_res.mean(),
        "a_res_std": a_res.std(),
        "a_res_max": a_res.max(),
        "a_res_min": a_res.min(),
        "a_res_range": a_res.max() - a_res.min(),
        "a_res_pico": a_res.max() - a_res.mean(),  # pico acima da média

        # --- Acelerações lineares (valores absolutos médios) ---
        "ax_mean": ax.mean(),
        "ay_mean": ay.mean(),
        "az_mean": az.mean(),
        "ax_std": ax.std(),
        "ay_std": ay.std(),
        "az_std": az.std(),
        "ax_max_abs": ax.abs().max(),
        "ay_max_abs": ay.abs().max(),
        "az_max_abs": az.abs().max(),

        # --- Giroscópio ---
        "gx_std": gx.std(),
        "gy_std": gy.std(),
        "gz_std": gz.std(),
        "gx_max_abs": gx.abs().max(),
        "gy_max_abs": gy.abs().max(),
        "gz_max_abs": gz.abs().max(),
        "gyro_magnitude_max": np.sqrt(gx**2 + gy**2 + gz**2).max(),

        # --- Detecção de queda ---
        # queda livre: a_res cai perto de 0g antes do impacto
        "a_res_min_below_05": (a_res < 0.5).sum(),  # amostras abaixo de 0.5g
        "a_res_min_below_03": (a_res < 0.3).sum(),  # amostras abaixo de 0.3g (quase queda livre)
        # impacto: picos altos
        "a_res_above_2g": (a_res > 2.0).sum(),
        "a_res_above_3g": (a_res > 3.0).sum(),
        "a_res_above_4g": (a_res > 4.0).sum(),

        # --- Variação brusca (jerk) ---
        "a_res_diff_max": a_res.diff().abs().max(),  # maior variação entre amostras consecutivas
        "a_res_diff_std": a_res.diff().abs().std(),

        # duração
        "duration_s": duration,
        "n_samples": len(df),
    }
    return features


def classify_mystery(mystery_features, known_features_by_class):
    """Classifica um ensaio misterioso por distância euclidiana das médias."""
    # features numéricas a usar para classificação
    feat_keys = [
        "a_res_mean", "a_res_std", "a_res_max", "a_res_range", "a_res_pico",
        "ax_std", "ay_std", "az_std",
        "gx_std", "gy_std", "gz_std",
        "gyro_magnitude_max",
        "a_res_min_below_05", "a_res_min_below_03",
        "a_res_above_2g", "a_res_above_3g",
        "a_res_diff_max", "a_res_diff_std",
    ]

    distances = {}
    for class_name, feats_list in known_features_by_class.items():
        # média das features da classe
        class_means = {}
        class_stds = {}
        for key in feat_keys:
            vals = [f[key] for f in feats_list]
            class_means[key] = np.mean(vals)
            class_stds[key] = np.std(vals) if np.std(vals) > 0 else 1.0

        # distância normalizada (z-score)
        dist = 0
        for key in feat_keys:
            diff = (mystery_features[key] - class_means[key]) / class_stds[key]
            dist += diff ** 2
        distances[class_name] = np.sqrt(dist)

    return distances


def main():
    # --- Carregar todos os ensaios ---
    known_classes = {
        "andando": [],
        "correndo": [],
        "caindo_frente": [],
        "caindo_joelho": [],
        "caindo_costas": [],
    }
    mystery_data = {}

    all_features = {}

    for dirname in sorted(os.listdir(DATA_DIR)):
        dirpath = os.path.join(DATA_DIR, dirname)
        if not os.path.isdir(dirpath):
            continue

        csv_path = os.path.join(dirpath, f"{dirname}.csv")
        if not os.path.exists(csv_path):
            continue

        df = load_csv(csv_path)
        feats = extract_features(df)
        all_features[dirname] = feats

        # classificar
        if dirname.startswith("adivinhe"):
            mystery_data[dirname] = {"df": df, "features": feats}
        else:
            for class_name in known_classes:
                if dirname.startswith(class_name):
                    known_classes[class_name].append(feats)
                    break

    # --- Tabela de features dos ensaios conhecidos ---
    print("=" * 80)
    print("📊 RESUMO DAS FEATURES POR CLASSE (média ± std)")
    print("=" * 80)

    key_features = [
        "a_res_mean", "a_res_std", "a_res_max", "a_res_range",
        "a_res_min_below_03", "a_res_above_2g", "a_res_above_3g",
        "a_res_diff_max", "gyro_magnitude_max",
    ]

    summary_rows = []
    for class_name, feats_list in known_classes.items():
        if not feats_list:
            continue
        row = {"classe": class_name}
        for key in key_features:
            vals = [f[key] for f in feats_list]
            row[key] = f"{np.mean(vals):.2f} ± {np.std(vals):.2f}"
        summary_rows.append(row)

    summary_df = pd.DataFrame(summary_rows).set_index("classe")
    print(summary_df.to_string())

    # --- Classificar ensaios misteriosos ---
    print("\n" + "=" * 80)
    print("🔮 CLASSIFICAÇÃO DOS ENSAIOS MISTERIOSOS")
    print("=" * 80)

    results = {}
    for name, data in sorted(mystery_data.items()):
        distances = classify_mystery(data["features"], known_classes)

        # ordenar por distância
        sorted_dist = sorted(distances.items(), key=lambda x: x[1])
        best_match = sorted_dist[0][0]
        results[name] = best_match

        print(f"\n{'─' * 50}")
        print(f"  {name}")
        print(f"{'─' * 50}")
        print(f"  Features-chave:")
        print(f"    a_res_max   = {data['features']['a_res_max']:.2f}g")
        print(f"    a_res_std   = {data['features']['a_res_std']:.2f}")
        print(f"    a_res_range = {data['features']['a_res_range']:.2f}g")
        print(f"    queda livre (< 0.3g) = {data['features']['a_res_min_below_03']} amostras")
        print(f"    impacto (> 2g)       = {data['features']['a_res_above_2g']} amostras")
        print(f"    impacto (> 3g)       = {data['features']['a_res_above_3g']} amostras")
        print(f"    gyro_max             = {data['features']['gyro_magnitude_max']:.1f}°/s")
        print(f"    jerk_max             = {data['features']['a_res_diff_max']:.2f}g/amostra")
        print()
        print(f"  Distâncias por classe:")
        for cls, dist in sorted_dist:
            marker = "  ◀ MELHOR MATCH" if cls == best_match else ""
            print(f"    {cls:20s}: {dist:8.2f}{marker}")

        print(f"\n  🎯 PALPITE: {name} = {best_match.upper()}")

    # --- Plot comparativo ---
    fig, axes = plt.subplots(3, 6, figsize=(24, 12))
    fig.suptitle("Comparação: Ensaios Conhecidos vs. Misteriosos", fontsize=16, fontweight="bold")

    # plotar ensaios conhecidos (colunas 0-4) e misteriosos (coluna 5 reservada)
    class_names = list(known_classes.keys())

    for col, class_name in enumerate(class_names):
        # pegar primeiro ensaio da classe como exemplo
        example_name = f"{class_name}_1"
        csv_path = os.path.join(DATA_DIR, example_name, f"{example_name}.csv")
        if not os.path.exists(csv_path):
            continue
        df = load_csv(csv_path)

        axes[0, col].plot(df["tempo_s"], df["a_res"], "k-", linewidth=0.5)
        axes[0, col].set_title(class_name, fontsize=10, fontweight="bold")
        axes[0, col].set_ylabel("a_res (g)" if col == 0 else "")
        axes[0, col].set_ylim(0, max(df["a_res"].max() * 1.1, 2))
        axes[0, col].axhline(y=1.0, color="red", linestyle=":", alpha=0.3)
        axes[0, col].grid(True, alpha=0.2)

        axes[1, col].plot(df["tempo_s"], df["ax"], linewidth=0.5, label="ax")
        axes[1, col].plot(df["tempo_s"], df["ay"], linewidth=0.5, label="ay")
        axes[1, col].plot(df["tempo_s"], df["az"], linewidth=0.5, label="az")
        axes[1, col].set_ylabel("accel (g)" if col == 0 else "")
        axes[1, col].grid(True, alpha=0.2)
        if col == 0:
            axes[1, col].legend(fontsize=7)

        g_mag = np.sqrt(df["gx"]**2 + df["gy"]**2 + df["gz"]**2)
        axes[2, col].plot(df["tempo_s"], g_mag, "m-", linewidth=0.5)
        axes[2, col].set_ylabel("gyro mag (°/s)" if col == 0 else "")
        axes[2, col].set_xlabel("tempo (s)")
        axes[2, col].grid(True, alpha=0.2)

    # plotar misteriosos na última coluna (empilhados)
    col = 5
    mystery_names = sorted(mystery_data.keys())
    colors = ["#e74c3c", "#2ecc71", "#3498db"]
    for i, (mname, mdata) in enumerate(sorted(mystery_data.items())):
        df = mdata["df"]
        axes[i, col].plot(df["tempo_s"], df["a_res"], color=colors[i], linewidth=0.5)
        prediction = results[mname]
        axes[i, col].set_title(f"{mname}\n→ {prediction}", fontsize=9, fontweight="bold",
                               color=colors[i])
        axes[i, col].axhline(y=1.0, color="red", linestyle=":", alpha=0.3)
        axes[i, col].grid(True, alpha=0.2)
        axes[i, col].set_xlabel("tempo (s)")

    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, "classificacao_comparativa.png"), dpi=150)
    print(f"\n📊 Gráfico salvo em: {DATA_DIR}/classificacao_comparativa.png")
    plt.show()

    # --- Resultado final ---
    print("\n" + "=" * 80)
    print("🏆 RESULTADO FINAL")
    print("=" * 80)
    for name, prediction in results.items():
        print(f"  {name} → {prediction.upper()}")
    print("=" * 80)


if __name__ == "__main__":
    main()
