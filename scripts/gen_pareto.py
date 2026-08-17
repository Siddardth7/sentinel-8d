#!/usr/bin/env python3
"""Generate the Line-Wide Defect & Non-Conformance Pareto Chart.

Saves to reports/figures/pareto.png.
"""
from __future__ import annotations

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def generate_pareto_chart(out_path: Path) -> None:
    """Build dual-axis Pareto chart of manufacturing non-conformances."""
    # Data extracted from CiP-DMD QC checks (802 assembled units)
    data = [
        {"mode": "Milling: Surface Roughness", "count": 179, "station": "CNC Milling", "is_final": False},
        {"mode": "Milling: Parallelism", "count": 67, "station": "CNC Milling", "is_final": False},
        {"mode": "Lathe: Coaxiality", "count": 59, "station": "CNC Lathe", "is_final": False},
        {"mode": "Assembly: Rework Required", "count": 52, "station": "Assembly", "is_final": True},
        {"mode": "Assembly: Pressure Out-of-Spec", "count": 19, "station": "Assembly", "is_final": True},
        {"mode": "Milling: Groove Diameter", "count": 19, "station": "CNC Milling", "is_final": False},
        {"mode": "Milling: Groove Depth", "count": 11, "station": "CNC Milling", "is_final": False},
        {"mode": "Lathe: Diameter Out-of-Spec", "count": 9, "station": "CNC Lathe", "is_final": False},
        {"mode": "Lathe: Length Out-of-Spec", "count": 1, "station": "CNC Lathe", "is_final": False},
    ]

    df = pd.DataFrame(data).sort_values("count", ascending=False).reset_index(drop=True)
    df["cum_count"] = df["count"].cumsum()
    df["cum_pct"] = df["cum_count"] / df["count"].sum() * 100

    fig, ax1 = plt.subplots(figsize=(12, 6.5))
    fig.patch.set_facecolor("#ffffff")
    ax1.set_facecolor("#fafbfc")

    x = np.arange(len(df))
    bar_colors = ["#d32f2f" if is_f else "#1976d2" for is_f in df["is_final"]]

    # Bar chart for defect counts
    bars = ax1.bar(
        x,
        df["count"],
        width=0.6,
        color=bar_colors,
        edgecolor="#263238",
        linewidth=1.0,
        alpha=0.85,
        zorder=2,
    )

    # Bar value labels
    for bar, count in zip(bars, df["count"]):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 2,
            f"{count}",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
            color="#263238",
        )

    ax1.set_ylabel("Defect / Non-Conformance Count", fontsize=11, fontweight="bold", color="#1a237e")
    ax1.set_xticks(x)
    ax1.set_xticklabels(df["mode"], rotation=35, ha="right", fontsize=9.5, fontweight="medium")
    ax1.set_ylim(0, max(df["count"]) * 1.15)
    ax1.grid(axis="y", linestyle="--", alpha=0.5, zorder=1)

    # Secondary axis for cumulative percentage line
    ax2 = ax1.twinx()
    ax2.plot(
        x,
        df["cum_pct"],
        color="#c2185b",
        marker="D",
        markersize=6,
        linewidth=2.2,
        label="Cumulative %",
        zorder=3,
    )
    ax2.set_ylabel("Cumulative Percentage (%)", fontsize=11, fontweight="bold", color="#c2185b")
    ax2.set_ylim(0, 105)
    ax2.axhline(80, color="#78909c", linestyle=":", linewidth=1.5, label="80% Threshold")

    # Percentage data points
    for idx, pct in enumerate(df["cum_pct"]):
        ax2.annotate(
            f"{pct:.1f}%",
            xy=(idx, pct),
            xytext=(0, 7),
            textcoords="offset points",
            ha="center",
            fontsize=8.5,
            fontweight="bold",
            color="#880e4f",
        )

    # Title & Subtitle
    plt.title(
        "Pareto Chart of Manufacturing Defects & Non-Conformances\n"
        r"$\bf{Target\ Failure\ Mode\ Selected:}$ Assembly Rework Required ($N=52/802 = 6.48\%$)",
        fontsize=13,
        fontweight="bold",
        color="#0d47a1",
        pad=15,
    )

    # Legend
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    legend_elements = [
        Patch(facecolor="#d32f2f", edgecolor="#263238", label="Final Assembly Defect (Target)"),
        Patch(facecolor="#1976d2", edgecolor="#263238", label="Upstream Station Non-Conformance"),
        Line2D([0], [0], color="#c2185b", marker="D", linewidth=2, label="Cumulative %"),
    ]
    ax1.legend(handles=legend_elements, loc="upper right", framealpha=0.95, fontsize=9.5)

    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved Pareto chart to {out_path}")


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "reports" / "figures" / "pareto.png"
    generate_pareto_chart(out)
