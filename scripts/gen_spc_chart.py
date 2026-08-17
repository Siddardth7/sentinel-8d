#!/usr/bin/env python3
"""Generate the Individual-Moving Range (I-MR) Statistical Process Control Chart.

Saves to reports/figures/spc_chart.png.
"""
from __future__ import annotations

import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add repo root for imports
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


def generate_spc_chart(out_path: Path) -> None:
    """Build dual-panel I-MR control chart on saw_weight with in-control limits."""
    parts_path = REPO_ROOT / "data" / "processed" / "parts.parquet"
    if not parts_path.exists():
        raise FileNotFoundError(f"Processed dataset not found at {parts_path}")

    parts = pd.read_parquet(parts_path)
    weights = parts["saw_weight"].dropna().values
    is_fail = parts["fail"].values[:len(weights)]

    # Compute 3-sigma control limits strictly from in-control (passing) parts
    in_control_weights = parts.loc[parts["fail"] == 0, "saw_weight"].dropna().values
    x_bar = float(np.mean(in_control_weights))
    mr_in_control = np.abs(np.diff(in_control_weights))
    mr_bar = float(np.mean(mr_in_control))
    d2 = 1.128

    sigma_hat = mr_bar / d2
    ucl_i = x_bar + 3 * sigma_hat
    lcl_i = x_bar - 3 * sigma_hat
    ucl_mr = 3.267 * mr_bar
    lcl_mr = 0.0

    # Moving range for full sequence
    mr_all = np.insert(np.abs(np.diff(weights)), 0, np.nan)
    subgroup = np.arange(1, len(weights) + 1)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 8.5), sharex=True, gridspec_kw={"height_ratios": [2.2, 1.3]})
    fig.patch.set_facecolor("#ffffff")

    # =========================================================================
    # Panel 1: Individuals (I) Chart
    # =========================================================================
    ax1.set_facecolor("#fafbfc")

    # Plot sequence line
    ax1.plot(subgroup, weights, color="#78909c", linewidth=0.9, alpha=0.7, zorder=1)

    # Plot points (Conforming vs Failing)
    pass_mask = is_fail == 0
    fail_mask = is_fail == 1

    ax1.scatter(subgroup[pass_mask], weights[pass_mask], color="#1976d2", s=14, alpha=0.6, label="Conforming Parts (Pass)", zorder=2)
    ax1.scatter(subgroup[fail_mask], weights[fail_mask], color="#d32f2f", marker="D", s=28, alpha=0.9, edgecolor="#b71c1c", label="Defective Units (Assembly Rework)", zorder=3)

    # Highlight out-of-control points (< LCL_I)
    ooc_mask = weights < lcl_i
    ax1.scatter(subgroup[ooc_mask], weights[ooc_mask], facecolor="none", edgecolor="#b71c1c", s=80, linewidth=1.6, label=f"Out of Control (< LCL = {lcl_i:.4f} kg)", zorder=4)

    # Control lines
    ax1.axhline(ucl_i, color="#d32f2f", linestyle="--", linewidth=1.5, label=f"UCL = {ucl_i:.4f} kg (+3σ)")
    ax1.axhline(x_bar, color="#2e7d32", linestyle="-", linewidth=1.8, label=f"Center Line ($\overline{{X}}$) = {x_bar:.4f} kg")
    ax1.axhline(lcl_i, color="#d32f2f", linestyle="--", linewidth=1.5, label=f"LCL = {lcl_i:.4f} kg (-3σ)")

    # Drawing Lower Spec Limit
    ax1.axhline(0.495, color="#78909c", linestyle=":", linewidth=1.2, label="Drawing LSL = 0.4950 kg")

    # Shaded in-control zone
    ax1.axhspan(lcl_i, ucl_i, color="#e8f5e9", alpha=0.3, zorder=0)

    ax1.set_title("Statistical Process Control (I-MR Chart) — Operation 10: Saw Cut Blank Weight (saw_weight)\n"
                  r"$\bf{Corrective\ Action\ (8D-D5):}$ In-Line 100% Scale Verification & Automatic Saw Interlock",
                  fontsize=12.5, fontweight="bold", color="#0d47a1", pad=12)
    ax1.set_ylabel("Individual Blank Weight (kg)", fontsize=10.5, fontweight="bold", color="#1a237e")
    ax1.set_ylim(0.485, 0.635)
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="upper right", ncol=2, framealpha=0.95, fontsize=8.5)

    # =========================================================================
    # Panel 2: Moving Range (MR) Chart
    # =========================================================================
    ax2.set_facecolor("#fafbfc")

    ax2.plot(subgroup, mr_all, color="#455a64", linewidth=1.0, marker="o", markersize=2.5, alpha=0.7, zorder=2)
    ax2.axhline(ucl_mr, color="#d32f2f", linestyle="--", linewidth=1.5, label=f"UCL_MR = {ucl_mr:.4f} kg")
    ax2.axhline(mr_bar, color="#2e7d32", linestyle="-", linewidth=1.6, label=f"$\overline{{MR}}$ = {mr_bar:.4f} kg")
    ax2.axhline(lcl_mr, color="#d32f2f", linestyle="--", linewidth=1.2, label=f"LCL_MR = {lcl_mr:.4f} kg")

    ax2.set_title("Moving Range Chart (n = 2)", fontsize=10.5, fontweight="bold", color="#0d47a1")
    ax2.set_xlabel("Sequential Part Production Order", fontsize=10.5, fontweight="bold", color="#1a237e")
    ax2.set_ylabel("Moving Range (kg)", fontsize=10.5, fontweight="bold", color="#1a237e")
    ax2.set_ylim(-0.005, max(np.nanmax(mr_all) * 1.15, ucl_mr * 1.1))
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(loc="upper right", framealpha=0.95, fontsize=8.5)

    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved SPC control chart to {out_path}")


if __name__ == "__main__":
    out = REPO_ROOT / "reports" / "figures" / "spc_chart.png"
    generate_spc_chart(out)
