#!/usr/bin/env python3
"""Generate the 'Smoking Gun' Root-Cause Isolation Figure.

Saves to reports/figures/smoking_gun.png.
"""
from __future__ import annotations

import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Add repo root for imports
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


def generate_smoking_gun_chart(out_path: Path) -> None:
    """Build dual-panel root-cause isolation figure for saw_weight."""
    parts_path = REPO_ROOT / "data" / "processed" / "parts.parquet"
    if not parts_path.exists():
        raise FileNotFoundError(f"Processed dataset not found at {parts_path}")

    parts = pd.read_parquet(parts_path)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.5))
    fig.patch.set_facecolor("#ffffff")

    # =========================================================================
    # Panel 1: Distribution Comparison (Pass vs Fail)
    # =========================================================================
    ax1.set_facecolor("#fafbfc")

    pass_weight = parts.loc[parts["fail"] == 0, "saw_weight"].dropna()
    fail_weight = parts.loc[parts["fail"] == 1, "saw_weight"].dropna()

    sns.kdeplot(
        pass_weight,
        ax=ax1,
        color="#1976d2",
        fill=True,
        alpha=0.35,
        linewidth=2.2,
        label=f"Pass (N = {len(pass_weight)}, Median = {pass_weight.median():.3f} kg)",
    )
    sns.kdeplot(
        fail_weight,
        ax=ax1,
        color="#d32f2f",
        fill=True,
        alpha=0.45,
        linewidth=2.2,
        label=f"Fail / Rework (N = {len(fail_weight)}, Median = {fail_weight.median():.3f} kg)",
    )

    # Threshold line at 0.540 kg
    ax1.axvline(0.540, color="#b71c1c", linestyle="--", linewidth=1.8, label="Critical Threshold: 0.540 kg")
    ax1.axvspan(0.48, 0.540, color="#ffebee", alpha=0.5, label="High Risk / Short Blank Zone")

    ax1.set_title("A. Distribution Shift: Saw Cut Blank Weight\nCohen's d = -0.752 (p = 1.0e-06)", fontsize=11.5, fontweight="bold", color="#0d47a1")
    ax1.set_xlabel("Saw Blank Weight (kg)", fontsize=10.5, fontweight="bold", color="#1a237e")
    ax1.set_ylabel("Density", fontsize=10.5, fontweight="bold", color="#1a237e")
    ax1.set_xlim(0.48, 0.63)
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="upper left", framealpha=0.95, fontsize=8.5)

    # =========================================================================
    # Panel 2: Defect Risk by Saw Weight Bins
    # =========================================================================
    ax2.set_facecolor("#fafbfc")

    # Create weight bins
    bins = [0.48, 0.53, 0.55, 0.57, 0.59, 0.63]
    labels = ["< 0.530 kg\n(Very Short)", "0.530–0.550 kg\n(Marginal)", "0.550–0.570 kg\n(Nominal -)", "0.570–0.590 kg\n(Nominal)", "> 0.590 kg\n(Nominal +)"]
    parts["weight_bin"] = pd.cut(parts["saw_weight"], bins=bins, labels=labels)

    bin_stats = parts.groupby("weight_bin", observed=False).agg(
        total=("fail", "count"),
        fails=("fail", "sum"),
    ).reset_index()
    bin_stats["defect_rate"] = bin_stats["fails"] / bin_stats["total"] * 100

    x = np.arange(len(bin_stats))
    bar_colors = ["#b71c1c" if i == 0 else "#e53935" if i == 1 else "#1976d2" for i in range(len(bin_stats))]

    bars = ax2.bar(
        x,
        bin_stats["defect_rate"],
        width=0.55,
        color=bar_colors,
        edgecolor="#263238",
        linewidth=1.0,
        alpha=0.88,
        zorder=2,
    )

    for bar, (_, row) in zip(bars, bin_stats.iterrows()):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.6,
            f"{row['defect_rate']:.1f}%\n({int(row['fails'])}/{int(row['total'])})",
            ha="center",
            va="bottom",
            fontsize=8.5,
            fontweight="bold",
            color="#263238",
        )

    ax2.axhline(6.48, color="#546e7a", linestyle=":", linewidth=1.5, label="Overall Baseline Rate (6.48%)")

    ax2.set_title("B. Defect Rate Surge in Undersized Saw Blanks\nOdds Ratio = 0.503 (95% CI: 0.371–0.683)", fontsize=11.5, fontweight="bold", color="#0d47a1")
    ax2.set_xlabel("Saw Cut Weight Interval", fontsize=10.5, fontweight="bold", color="#1a237e")
    ax2.set_ylabel("Assembly Defect / Rework Rate (%)", fontsize=10.5, fontweight="bold", color="#1a237e")
    ax2.set_xticks(x)
    ax2.set_xticklabels(bin_stats["weight_bin"], fontsize=9)
    ax2.set_ylim(0, max(bin_stats["defect_rate"]) * 1.25)
    ax2.grid(axis="y", linestyle="--", alpha=0.5, zorder=1)
    ax2.legend(loc="upper right", framealpha=0.95, fontsize=8.5)

    # Supertitle
    plt.suptitle(
        "Root Cause Confirmation: Saw Blank Weight Deficit Drives Downstream Assembly Failure",
        fontsize=13.5,
        fontweight="bold",
        color="#0d47a1",
        y=0.98,
    )

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved smoking gun chart to {out_path}")


if __name__ == "__main__":
    out = REPO_ROOT / "reports" / "figures" / "smoking_gun.png"
    generate_smoking_gun_chart(out)
