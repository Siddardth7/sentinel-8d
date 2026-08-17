#!/usr/bin/env python3
"""Generate the Univariate Effect Size Ranking Chart.

Saves to reports/figures/univariate_ranking.png.
"""
from __future__ import annotations

import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add repo root to path for imports
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from src import stats


def generate_univariate_ranking_chart(out_path: Path) -> None:
    """Build horizontal bar chart of univariate effect sizes."""
    parts_path = REPO_ROOT / "data" / "processed" / "parts.parquet"
    if not parts_path.exists():
        raise FileNotFoundError(f"Processed dataset not found at {parts_path}")

    parts = pd.read_parquet(parts_path)
    ranking = stats.univariate_screen(parts, target="fail", alpha=0.05)

    # Filter to process/measurement predictors (excluding missing indicators for the plot)
    plot_df = ranking.loc[
        ~ranking["parameter"].str.endswith("_missing")
    ].sort_values("abs_effect_size", ascending=True).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(11, 6.5))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#fafbfc")

    y = np.arange(len(plot_df))
    colors = [
        "#d32f2f" if sig else "#78909c"
        for sig in plot_df["significant_fdr"]
    ]

    bars = ax.barh(
        y,
        plot_df["abs_effect_size"],
        height=0.6,
        color=colors,
        edgecolor="#263238",
        linewidth=1.0,
        alpha=0.88,
        zorder=2,
    )

    # Value annotations on bars
    for idx, (bar, row) in enumerate(zip(bars, plot_df.itertuples())):
        effect_str = f"{row.effect_size_type}: {row.effect_size:+.3f}"
        p_str = f" (pFDR = {row.p_fdr_bh:.1e})" if row.significant_fdr else " (n.s.)"
        ax.text(
            bar.get_width() + 0.03,
            bar.get_y() + bar.get_height() / 2,
            f"{effect_str}{p_str}",
            ha="left",
            va="center",
            fontsize=8.5,
            fontweight="bold" if row.significant_fdr else "normal",
            color="#0d47a1" if row.significant_fdr else "#546e7a",
        )

    ax.set_yticks(y)
    ax.set_yticklabels(plot_df["parameter"], fontsize=9.5, fontweight="medium")
    ax.set_xlabel("Absolute Effect Size (|Cohen's d| or Cramér's V)", fontsize=11, fontweight="bold", color="#1a237e")
    ax.set_xlim(0, max(plot_df["abs_effect_size"]) * 1.35)
    ax.grid(axis="x", linestyle="--", alpha=0.5, zorder=1)

    # Reference lines for effect size interpretation
    ax.axvline(0.2, color="#f57c00", linestyle=":", linewidth=1.5, label="Small Effect Threshold (|d| = 0.20)")
    ax.axvline(0.5, color="#d32f2f", linestyle=":", linewidth=1.5, label="Medium Effect Threshold (|d| = 0.50)")

    # Title
    plt.title(
        "Univariate Screening Ranking (Pass vs. Fail Rejection Separation)\n"
        r"$\bf{Benjamini–Hochberg\ FDR\ Controlled\ (\alpha = 0.05)}$",
        fontsize=13,
        fontweight="bold",
        color="#0d47a1",
        pad=15,
    )

    # Legend
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    legend_elements = [
        Patch(facecolor="#d32f2f", edgecolor="#263238", label="Significant after FDR Correction (pFDR < 0.05)"),
        Patch(facecolor="#78909c", edgecolor="#263238", label="Not Significant after FDR Correction"),
        Line2D([0], [0], color="#f57c00", linestyle=":", linewidth=1.5, label="Small Effect (|d| ≥ 0.2)"),
        Line2D([0], [0], color="#d32f2f", linestyle=":", linewidth=1.5, label="Medium Effect (|d| ≥ 0.5)"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", framealpha=0.95, fontsize=9)

    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved univariate ranking chart to {out_path}")


if __name__ == "__main__":
    out = REPO_ROOT / "reports" / "figures" / "univariate_ranking.png"
    generate_univariate_ranking_chart(out)
