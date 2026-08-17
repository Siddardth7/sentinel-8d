#!/usr/bin/env python3
"""Generate the CiP-DMD manufacturing process flow diagram.

Saves to reports/figures/process_flow.png.
"""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt


def _draw_box(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    label: str,
    sublabel: str = "",
    color: str = "#bbdefb",
    fontsize: int = 11,
) -> None:
    """Draw a rounded process step box."""
    rect = patches.FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.15",
        facecolor=color,
        edgecolor="#37474f",
        linewidth=1.5,
    )
    ax.add_patch(rect)
    ax.text(
        x + w / 2,
        y + h / 2 + (0.15 if sublabel else 0.0),
        label,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight="bold",
        color="#1a237e",
    )
    if sublabel:
        ax.text(
            x + w / 2,
            y + h / 2 - 0.25,
            sublabel,
            ha="center",
            va="center",
            fontsize=8,
            color="#455a64",
            style="italic",
        )


def _draw_qc_box(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    label: str,
    measurements: Sequence[str],
    color: str = "#c8e6c9",
) -> None:
    """Draw a dashed QC measurement checkpoint box."""
    rect = patches.FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.1",
        facecolor=color,
        edgecolor="#2e7d32",
        linewidth=1.2,
        linestyle="--",
    )
    ax.add_patch(rect)
    ax.text(
        x + w / 2,
        y + h - 0.22,
        label,
        ha="center",
        va="center",
        fontsize=9,
        fontweight="bold",
        color="#1b5e20",
    )
    for i, m in enumerate(measurements):
        if not m:
            continue
        ax.text(
            x + w / 2,
            y + h - 0.5 - i * 0.2,
            m,
            ha="center",
            va="center",
            fontsize=7,
            color="#33691e",
            family="monospace",
        )


def _draw_arrow(
    ax: plt.Axes,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    color: str = "#455a64",
) -> None:
    """Draw an arrow from (x1, y1) to (x2, y2)."""
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=2),
    )


def draw_process_flow(out_path: Path) -> None:
    """Draw boxes-and-arrows process flow for the CiP-DMD manufacturing line."""
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("#fafafa")

    # --- Color palette ---
    raw_color = "#e8eaf6"      # indigo-50
    station_color = "#bbdefb"  # blue-100
    qc_color = "#c8e6c9"      # green-100
    final_color = "#fff9c4"    # yellow-100

    # === Title ===
    ax.text(
        8,
        8.6,
        "CiP-DMD Manufacturing Process Flow",
        ha="center",
        va="center",
        fontsize=16,
        fontweight="bold",
        color="#0d47a1",
    )
    ax.text(
        8,
        8.25,
        "Center for Industrial Productivity — Discrete Manufacturing Dataset (TU Darmstadt)",
        ha="center",
        va="center",
        fontsize=9,
        color="#546e7a",
    )

    # ==========================
    # CYLINDER BOTTOM PATH (top)
    # ==========================
    ax.text(
        0.5,
        7.4,
        "Cylinder Bottom Path",
        fontsize=10,
        fontweight="bold",
        color="#1565c0",
        style="italic",
    )

    # Raw material
    _draw_box(ax, 0.3, 6.2, 1.8, 0.9, "Raw\nMaterial", "Steel bar stock", raw_color, 10)
    _draw_arrow(ax, 2.1, 6.65, 2.9, 6.65)

    # Saw station
    _draw_box(ax, 2.9, 6.2, 2.0, 0.9, "Saw", "Kasto SBA 2", station_color)
    _draw_qc_box(
        ax,
        2.9,
        4.9,
        2.0,
        1.1,
        "QC: Saw",
        ["weight (0.495-0.641 kg)", "anomaly (0,1)"],
        qc_color,
    )
    ax.annotate(
        "",
        xy=(3.9, 5.9),
        xytext=(3.9, 6.2),
        arrowprops=dict(arrowstyle="-|>", color="#2e7d32", lw=1.5, ls="--"),
    )

    _draw_arrow(ax, 4.9, 6.65, 5.8, 6.65)

    # CNC Milling station
    _draw_box(ax, 5.8, 6.2, 2.3, 0.9, "CNC Milling", "DMC 50H", station_color)
    _draw_qc_box(
        ax,
        5.8,
        4.2,
        2.3,
        1.8,
        "QC: CNC Milling",
        [
            "surface_roughness (<=2.5 um)",
            "parallelism (<=0.1 mm)",
            "groove_depth (0.75-0.85 mm)",
            "groove_diameter (39.91-40.0 mm)",
            "anomaly (0,1,2,3)",
        ],
        qc_color,
    )
    ax.annotate(
        "",
        xy=(6.95, 5.9),
        xytext=(6.95, 6.2),
        arrowprops=dict(arrowstyle="-|>", color="#2e7d32", lw=1.5, ls="--"),
    )

    # Arrow to assembly
    _draw_arrow(ax, 8.1, 6.65, 9.5, 5.2)

    # ============================
    # PISTON ROD PATH (bottom)
    # ============================
    ax.text(
        0.5,
        3.4,
        "Piston Rod Path",
        fontsize=10,
        fontweight="bold",
        color="#1565c0",
        style="italic",
    )

    # Raw material
    _draw_box(ax, 0.3, 2.2, 1.8, 0.9, "Raw\nMaterial", "Steel rod stock", raw_color, 10)
    _draw_arrow(ax, 2.1, 2.65, 2.9, 2.65)

    # CNC Lathe station
    _draw_box(ax, 2.9, 2.2, 2.2, 0.9, "CNC Lathe", "Index C65", station_color)
    _draw_qc_box(
        ax,
        2.9,
        0.5,
        2.2,
        1.5,
        "QC: CNC Lathe",
        [
            "coaxiality (<=50 um)",
            "diameter (+/-0.018 mm)",
            "length (163.45-163.75 mm)",
        ],
        qc_color,
    )
    ax.annotate(
        "",
        xy=(4.0, 2.0),
        xytext=(4.0, 2.2),
        arrowprops=dict(arrowstyle="-|>", color="#2e7d32", lw=1.5, ls="--"),
    )

    # Arrow to assembly
    _draw_arrow(ax, 5.1, 2.65, 9.5, 4.2)

    # ============================
    # ASSEMBLY + FINAL QC (right)
    # ============================
    _draw_box(ax, 9.5, 3.8, 2.3, 1.6, "Assembly", "Cylinder\nassembly", final_color, 12)
    _draw_arrow(ax, 11.8, 4.6, 12.5, 4.6)

    # Final QC
    _draw_qc_box(
        ax,
        12.5,
        3.7,
        2.5,
        1.8,
        "Final QC: Assembly",
        [
            "pressure (7564-16486 N)",
            "rework (y/n) <- FAIL LABEL",
        ],
        qc_color,
    )

    _draw_arrow(ax, 15.0, 4.6, 15.5, 4.6)

    # Final product
    _draw_box(ax, 15.2, 4.0, 0.6, 1.2, "OK", "", "#e8f5e9", 14)

    # ============================
    # ANOMALY LEGEND
    # ============================
    legend_y = 0.8
    ax.text(
        8.0,
        legend_y + 0.8,
        "Anomaly Classes (intentionally provoked):",
        fontsize=9,
        fontweight="bold",
        color="#b71c1c",
    )
    anomalies = [
        "0 = Normal process",
        "1 = Raw material badly aligned at saw -> cut too short -> anomalous milling",
        "2 = Part unevenly clamped in milling jig -> anomalous milling",
        "3 = Miscellaneous errors (not visible in process data)",
    ]
    for i, a in enumerate(anomalies):
        ax.text(
            8.2,
            legend_y + 0.4 - i * 0.25,
            a,
            fontsize=7.5,
            color="#c62828",
            family="monospace",
        )

    # ============================
    # KEY STATS
    # ============================
    ax.text(
        12.5,
        2.8,
        "Dataset: 802 assembled cylinders",
        fontsize=9,
        fontweight="bold",
        color="#37474f",
    )
    ax.text(
        12.5,
        2.45,
        "985 cylinder bottoms (saw) -> 845 (milled) -> 802 assembled",
        fontsize=7.5,
        color="#546e7a",
    )
    ax.text(
        12.5,
        2.15,
        "898 piston rods (lathe QC: 673) -> 802 assembled",
        fontsize=7.5,
        color="#546e7a",
    )
    ax.text(
        12.5,
        1.85,
        "Failure rate: 52/802 = 6.5% (rework required)",
        fontsize=7.5,
        fontweight="bold",
        color="#c62828",
    )

    # Join key annotation
    ax.text(
        9.0,
        3.3,
        "Join keys:\npart_id_cylinder_bottom\npart_id_piston_rod",
        fontsize=7,
        color="#6a1b9a",
        style="italic",
        bbox=dict(
            boxstyle="round,pad=0.3",
            facecolor="#f3e5f5",
            edgecolor="#6a1b9a",
            alpha=0.8,
        ),
    )

    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Saved process flow diagram to {out_path}")


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "reports" / "figures" / "process_flow.png"
    draw_process_flow(out)

