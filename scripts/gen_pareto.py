#!/usr/bin/env python3
"""Generate the Line-Wide Defect & Non-Conformance Pareto Chart.

Every count is derived directly from ``data/processed/parts.parquet`` — the
per-station ``*_qcpass`` flags and the binary ``fail`` target — so the figure is
fully reproducible from the data pipeline with no hard-coded numbers.

Saves to reports/figures/pareto.png.
"""
from __future__ import annotations

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]

# Each failure mode maps to a source column in parts.parquet. Upstream station
# non-conformances are the `*_qcpass` flags (a failure is qc_pass == False); the
# final assembly target is the `fail` label. `is_final` drives the red/blue split.
PARETO_SPEC = [
    ("Milling: Surface Roughness",     "mill_surface_roughness_qcpass", "CNC Milling", False),
    ("Milling: Parallelism",           "mill_parallelism_qcpass",       "CNC Milling", False),
    ("Milling: Groove Diameter",       "mill_groove_diameter_qcpass",   "CNC Milling", False),
    ("Milling: Groove Depth",          "mill_groove_depth_qcpass",      "CNC Milling", False),
    ("Lathe: Coaxiality",              "lathe_coaxiality_qcpass",       "CNC Lathe",   False),
    ("Lathe: Diameter Out-of-Spec",    "lathe_diameter_qcpass",         "CNC Lathe",   False),
    ("Lathe: Length Out-of-Spec",      "lathe_length_qcpass",           "CNC Lathe",   False),
    ("Assembly: Pressure Out-of-Spec", "assembly_pressure_qcpass",      "Assembly",    True),
    ("Assembly: Rework Required",      "fail",                          "Assembly",    True),
]


def _count_failures(parts: pd.DataFrame, col: str) -> int:
    """Number of parts flagged as a QC failure for `col`.

    `fail` is the binary target (1 = reject); every other column is a `*_qcpass`
    boolean where a failure is `qc_pass == False`. `== False` ignores NaN.
    """
    if col == "fail":
        return int((parts[col] == 1).sum())
    return int((parts[col] == False).sum())


def build_pareto_frame(parts: pd.DataFrame) -> pd.DataFrame:
    """Derive the ranked Pareto table (mode, count, station, is_final) from data."""
    rows = [
        {"mode": mode, "count": _count_failures(parts, col),
         "station": station, "is_final": is_final}
        for mode, col, station, is_final in PARETO_SPEC
        if col in parts.columns
    ]
    df = pd.DataFrame(rows).sort_values("count", ascending=False).reset_index(drop=True)
    df["cum_count"] = df["count"].cumsum()
    df["cum_pct"] = df["cum_count"] / df["count"].sum() * 100
    return df


def generate_pareto_chart(out_path: Path, parts_path: Path) -> None:
    """Build dual-axis Pareto chart of manufacturing non-conformances."""
    parts = pd.read_parquet(parts_path)
    df = build_pareto_frame(parts)

    # Target failure mode = the final assembly reject (`fail`), for the subtitle.
    n_total = len(parts)
    n_target = int((parts["fail"] == 1).sum())
    target_pct = n_target / n_total * 100

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
    ax1.set_xticklabels(df["mode"], rotation=35, ha="right", fontsize=9.5)
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

    # Title & Subtitle (target stats derived from the data)
    plt.title(
        "Pareto Chart of Manufacturing Defects & Non-Conformances\n"
        r"$\bf{Target\ Failure\ Mode\ Selected:}$ Assembly Rework Required "
        f"($N={n_target}/{n_total} = {target_pct:.2f}\\%$)",
        fontsize=13,
        fontweight="bold",
        color="#0d47a1",
        pad=15,
    )

    # Legend — anchored in the empty block above the small right-hand bars, clear
    # of the near-100% cumulative labels crowding the top-right corner.
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    legend_elements = [
        Patch(facecolor="#d32f2f", edgecolor="#263238", label="Final Assembly Defect (Target)"),
        Patch(facecolor="#1976d2", edgecolor="#263238", label="Upstream Station Non-Conformance"),
        Line2D([0], [0], color="#c2185b", marker="D", linewidth=2, label="Cumulative %"),
    ]
    ax1.legend(
        handles=legend_elements,
        loc="center right",
        bbox_to_anchor=(0.995, 0.42),
        framealpha=0.95,
        fontsize=9.5,
    )

    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved Pareto chart to {out_path}")


if __name__ == "__main__":
    out = REPO_ROOT / "reports" / "figures" / "pareto.png"
    parts = REPO_ROOT / "data" / "processed" / "parts.parquet"
    generate_pareto_chart(out, parts)
