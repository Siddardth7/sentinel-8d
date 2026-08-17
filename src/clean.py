"""Stage 2 — cleaning & tidying to one row per part.

Covers execution.md §4 (Step 2). Implemented on Day 2.

Output contract: a tidy frame with one row per finished (assembled) cylinder,
one column per upstream parameter, plus a single binary `fail` column.
Persisted to data/processed/parts.parquet so later stages never re-parse raw data.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"


def tidy_one_row_per_part(
    raw: dict[str, pd.DataFrame],
    data_dict: pd.DataFrame,
) -> pd.DataFrame:
    """Reshape raw data into one row per assembled cylinder.

    Join logic (CiP-DMD):
        assembly_qc (802 rows) is the spine table.
        Left-join saw_qc       on part_id_cylinder_bottom == part_id  → saw_weight
        Left-join mill_qc      on part_id_cylinder_bottom == part_id  → mill_* measurements
        Left-join lathe_qc     on part_id_piston_rod      == part_id  → lathe_* measurements
        Left-join cb_meta      on part_id_cylinder_bottom == part_id  → saw/mill anomaly + qc_pass
        Left-join pr_meta      on part_id_piston_rod      == part_id  → lathe anomaly + qc_pass
    """
    # --- Start from assembly QC as the spine (802 assembled cylinders) ---
    parts = raw["assembly_qc"].copy()

    # Rename assembly columns with station prefix
    parts = parts.rename(columns={
        "rework": "assembly_rework",
        "pressure": "assembly_pressure",
    })

    # --- Join saw QC (weight + anomaly from CSV) ---
    saw = raw["saw_qc"].copy()
    saw = saw.rename(columns={
        "weight": "saw_weight",
        "anomaly": "saw_anomaly_csv",
    })
    saw = saw.drop(columns=["part_id"], errors="ignore")
    # Need part_id for join — re-add from original
    saw["part_id"] = raw["saw_qc"]["part_id"]
    parts = parts.merge(
        saw[["part_id", "saw_weight", "saw_anomaly_csv"]],
        left_on="part_id_cylinder_bottom",
        right_on="part_id",
        how="left",
    ).drop(columns=["part_id"])

    # --- Join milling QC (4 measurements) ---
    mill = raw["mill_qc"].copy()
    mill = mill.rename(columns={
        "surface_roughness": "mill_surface_roughness",
        "parallelism": "mill_parallelism",
        "groove_depth": "mill_groove_depth",
        "groove_diameter": "mill_groove_diameter",
    })
    parts = parts.merge(
        mill.rename(columns={"part_id": "part_id_join"}),
        left_on="part_id_cylinder_bottom",
        right_on="part_id_join",
        how="left",
    ).drop(columns=["part_id_join"])

    # --- Join lathe QC (3 measurements) ---
    lathe = raw["lathe_qc"].copy()
    lathe = lathe.rename(columns={
        "coaxiality": "lathe_coaxiality",
        "diameter": "lathe_diameter",
        "length": "lathe_length",
    })
    parts = parts.merge(
        lathe.rename(columns={"part_id": "part_id_join"}),
        left_on="part_id_piston_rod",
        right_on="part_id_join",
        how="left",
    ).drop(columns=["part_id_join"])

    # --- Join cylinder_bottom metadata (anomaly classes + qc_pass) ---
    cb_meta = raw["cb_meta"].copy()
    parts = parts.merge(
        cb_meta.rename(columns={"part_id": "part_id_join"}),
        left_on="part_id_cylinder_bottom",
        right_on="part_id_join",
        how="left",
    ).drop(columns=["part_id_join"])

    # --- Join piston_rod metadata (anomaly + qc_pass) ---
    pr_meta = raw["pr_meta"].copy()
    parts = parts.merge(
        pr_meta.rename(columns={"part_id": "part_id_join"}),
        left_on="part_id_piston_rod",
        right_on="part_id_join",
        how="left",
    ).drop(columns=["part_id_join"])

    # --- Consolidate anomaly columns ---
    # Prefer metadata anomaly over CSV anomaly (they should agree)
    if "saw_anomaly" in parts.columns and "saw_anomaly_csv" in parts.columns:
        # Fill metadata NaNs with CSV values
        parts["saw_anomaly"] = parts["saw_anomaly"].fillna(parts["saw_anomaly_csv"])
        parts = parts.drop(columns=["saw_anomaly_csv"])
    elif "saw_anomaly_csv" in parts.columns:
        parts = parts.rename(columns={"saw_anomaly_csv": "saw_anomaly"})

    # --- Enforce numeric dtypes for continuous columns ---
    continuous_cols = data_dict.loc[
        data_dict["dtype"] == "continuous", "column"
    ].tolist()
    for col in continuous_cols:
        if col in parts.columns:
            parts[col] = pd.to_numeric(parts[col], errors="coerce")

    # --- Drop zero-variance columns ---
    # (They carry no signal and break VIF on Day 4)
    numeric_cols = parts.select_dtypes(include=[np.number]).columns
    zero_var = [c for c in numeric_cols if parts[c].std() == 0]
    if zero_var:
        print(f"  tidy: dropping {len(zero_var)} zero-variance column(s): {zero_var}")
        parts = parts.drop(columns=zero_var)

    print(f"  tidy: result → {parts.shape[0]} rows × {parts.shape[1]} cols")
    return parts


def handle_missing(df: pd.DataFrame, max_missing_frac: float = 0.5) -> pd.DataFrame:
    """Quantify and handle missing values.

    Rule of thumb (execution.md §4): drop columns above `max_missing_frac`
    missing. For the rest, DO NOT blindly impute — missingness can be
    informative (a station a part never visited). Prefer adding a
    `<col>_missing` indicator column over silent imputation.
    """
    parts = df.copy()

    # --- Report per-column missingness ---
    miss = parts.isnull().sum()
    miss_pct = (miss / len(parts) * 100).round(1)
    miss_report = pd.DataFrame({
        "missing_count": miss,
        "missing_pct": miss_pct,
    }).sort_values("missing_pct", ascending=False)

    print("\n  === Missing Value Report ===")
    has_missing = miss_report[miss_report["missing_count"] > 0]
    if has_missing.empty:
        print("  No missing values found.")
    else:
        for idx, row in has_missing.iterrows():
            print(f"    {idx:35s}  {int(row['missing_count']):>4d} ({row['missing_pct']:.1f}%)")

    # --- Drop columns above threshold ---
    high_miss = miss_pct[miss_pct > max_missing_frac * 100].index.tolist()
    if high_miss:
        print(f"\n  Dropping {len(high_miss)} column(s) with >{max_missing_frac*100:.0f}% missing: {high_miss}")
        parts = parts.drop(columns=high_miss)

    # --- Add missing indicators + median fill for remaining missing ---
    numeric_cols = parts.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        n_miss = parts[col].isnull().sum()
        if n_miss > 0:
            # Missingness indicator (informative: station not visited)
            parts[f"{col}_missing"] = parts[col].isnull().astype(int)
            # Fill with median
            median_val = parts[col].median()
            parts[col] = parts[col].fillna(median_val)
            print(f"    {col}: filled {n_miss} NaN with median={median_val:.4f}, added indicator")

    print(f"  handle_missing: result → {parts.shape[0]} rows × {parts.shape[1]} cols")
    return parts


def define_label(df: pd.DataFrame) -> pd.DataFrame:
    """Add the binary target `fail` (1 = final-QC reject: assembly rework required).

    The specific failing characteristic to chase is chosen on Day 3 from the
    Pareto (execution.md §5). For the first pass, `fail` encodes whether the
    assembled cylinder required rework — the most direct assembly-level failure.
    """
    parts = df.copy()

    # Binary label: rework == "y" → fail = 1
    parts["fail"] = (parts["assembly_rework"] == "y").astype(int)

    # Sanity check
    n_fail = parts["fail"].sum()
    n_total = len(parts)
    rate = n_fail / n_total * 100
    print(f"\n  === Label Definition ===")
    print(f"    fail = 1 where assembly_rework == 'y'")
    print(f"    Failures: {n_fail}/{n_total} = {rate:.1f}%")

    return parts


def save_processed(df: pd.DataFrame, name: str = "parts.parquet") -> Path:
    """Write the tidy table to data/processed/ and return its path."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = PROCESSED_DIR / name
    df.to_parquet(out, index=False)
    return out

