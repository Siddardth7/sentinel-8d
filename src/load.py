"""Stage 1 — data acquisition & schema mapping.

Design goal: everything downstream is *dataset-agnostic*. Only this module knows
the layout of the raw CiP-DMD source — it returns raw DataFrames plus a data
dictionary, and the rest of the pipeline works on those.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

# Project-root-relative paths. src/ is one level below the repo root.
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


# ---------------------------------------------------------------------------
# Internal helpers for CiP-DMD metadata parsing
# ---------------------------------------------------------------------------

def _parse_cb_meta(path: Path) -> pd.DataFrame:
    """Parse cylinder_bottom meta_data.json into a flat DataFrame.

    Extracts per-part: part_id, anomaly class per station (saw, cnc_milling),
    and qc_pass per quality measurement.
    """
    with open(path) as fp:
        entries = json.load(fp)

    rows = []
    for e in entries:
        pid = str(e["part_id"])
        row: dict = {"part_id": int(pid)}

        # Anomaly classes from process_data
        for pd_item in e.get("process_data", []):
            name = pd_item.get("name", "")
            anomaly = pd_item.get("anomaly", 0)
            # Normalize string anomaly values to int
            try:
                anomaly = int(anomaly)
            except (ValueError, TypeError):
                anomaly = 0
            if "saw" in name:
                row["saw_anomaly"] = anomaly
            elif "milling" in name:
                row["mill_anomaly"] = anomaly

        # qc_pass flags from quality_data
        for qd in e.get("quality_data", []):
            process = qd.get("process", "")
            for m in qd.get("measurements", []):
                feat = m["feature"]
                qc = m.get("qc_pass", True)
                if "saw" in process:
                    row[f"saw_{feat}_qcpass"] = bool(qc)
                elif "mill" in process or "cnc_mill" in process:
                    row[f"mill_{feat}_qcpass"] = bool(qc)

        rows.append(row)

    df = pd.DataFrame(rows)
    # Deduplicate: part_id 103604 appears twice in the raw JSON
    df = df.drop_duplicates(subset="part_id", keep="first")
    return df


def _parse_pr_meta(path: Path) -> pd.DataFrame:
    """Parse piston_rod meta_data.json into a flat DataFrame."""
    with open(path) as fp:
        entries = json.load(fp)

    rows = []
    for e in entries:
        pid = str(e["part_id"])
        row: dict = {"part_id": int(pid)}

        # Anomaly from process_data (piston rods have cnc_lathe)
        for pd_item in e.get("process_data", []):
            anomaly = pd_item.get("anomaly", 0)
            try:
                anomaly = int(anomaly)
            except (ValueError, TypeError):
                anomaly = 0
            row["lathe_anomaly"] = anomaly

        # qc_pass flags
        for qd in e.get("quality_data", []):
            for m in qd.get("measurements", []):
                feat = m["feature"]
                qc = m.get("qc_pass", True)
                row[f"lathe_{feat}_qcpass"] = bool(qc)

        rows.append(row)

    return pd.DataFrame(rows)


def _parse_cyl_meta(path: Path) -> pd.DataFrame:
    """Parse cylinder (assembly) meta_data.json to get component ID mapping.

    Returns a DataFrame with columns:
        cylinder_id, part_id_cylinder_bottom, part_id_piston_rod,
        assembly_rework_qcpass, assembly_pressure_qcpass
    """
    with open(path) as fp:
        entries = json.load(fp)

    rows = []
    for e in entries:
        cid = str(e["part_id"])
        comp_ids = e.get("component_ids", [])
        row: dict = {"cylinder_id": cid}

        # component_ids: first entry uses labels, rest have actual IDs
        if len(comp_ids) == 2:
            cb_id = comp_ids[0]
            pr_id = comp_ids[1]
            # Skip the header row that has labels instead of IDs
            if cb_id.startswith("part_id"):
                continue
            row["part_id_cylinder_bottom"] = int(cb_id)
            row["part_id_piston_rod"] = int(pr_id)

        # qc_pass from quality_data
        for qd in e.get("quality_data", []):
            for m in qd.get("measurements", []):
                feat = m["feature"]
                qc = m.get("qc_pass", True)
                row[f"assembly_{feat}_qcpass"] = bool(qc)

        rows.append(row)

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_raw(dataset: str) -> dict[str, pd.DataFrame]:
    """Read the untouched download from data/raw/ into DataFrames.

    Parameters
    ----------
    dataset : {"cip_dmd", "bosch"}
        Which source is in hand. Set on Day 1 by the data access gate.

    Returns
    -------
    dict[str, pd.DataFrame]
        For CiP-DMD, returns a dict with keys:
            saw_qc, mill_qc, lathe_qc, assembly_qc,
            cb_meta, pr_meta, cyl_meta
        Each value is a DataFrame ready for joining in clean.tidy_one_row_per_part.
    """
    if dataset == "cip_dmd":
        return _load_cip_dmd()
    elif dataset == "bosch":
        raise NotImplementedError(
            "Bosch fallback not needed — CiP-DMD data acquired on Day 1."
        )
    else:
        raise ValueError(f"Unknown dataset: {dataset!r}. Expected 'cip_dmd' or 'bosch'.")


def _load_cip_dmd() -> dict[str, pd.DataFrame]:
    """Load all CiP-DMD quality CSVs and metadata JSONs."""
    raw: dict[str, pd.DataFrame] = {}

    # ---- Quality CSVs (semicolon-separated) ----
    raw["saw_qc"] = pd.read_csv(
        RAW_DIR / "saw" / "quality_data" / "quality_data.csv", sep=";"
    )
    raw["mill_qc"] = pd.read_csv(
        RAW_DIR / "quality_data" / "quality_data.csv", sep=";"
    )
    raw["lathe_qc"] = pd.read_csv(
        RAW_DIR / "piston_rod" / "cnc_lathe" / "quality_data" / "quality_data.csv",
        sep=";",
    )
    raw["assembly_qc"] = pd.read_csv(
        RAW_DIR / "cylinder" / "assembly" / "quality_data" / "quality_data.csv",
        sep=";",
    )

    # ---- Metadata JSONs → flat DataFrames ----
    raw["cb_meta"] = _parse_cb_meta(RAW_DIR / "meta_data.json")
    raw["pr_meta"] = _parse_pr_meta(RAW_DIR / "piston_rod" / "meta_data.json")
    raw["cyl_meta"] = _parse_cyl_meta(RAW_DIR / "cylinder" / "meta_data.json")

    # ---- Deduplicate on part_id where needed ----
    # saw_qc has part_id 103604 twice; keep first to prevent 1:many joins
    for key in ("saw_qc", "mill_qc", "lathe_qc"):
        id_col = "part_id"
        if id_col in raw[key].columns:
            before = len(raw[key])
            raw[key] = raw[key].drop_duplicates(subset=id_col, keep="first")
            after = len(raw[key])
            if before != after:
                print(f"  load_raw: deduplicated {key}: {before} → {after} rows")

    # Quick sanity prints
    for name, df in raw.items():
        print(f"  load_raw: {name:15s} → {df.shape[0]:>5d} rows × {df.shape[1]:>3d} cols")

    return raw


def map_schema(raw: dict[str, pd.DataFrame], dataset: str) -> pd.DataFrame:
    """Build the data dictionary: one row per measurement column.

    Columns of the returned frame:
        column, station, parameter, dtype (continuous/categorical),
        units, role (id | process | quality)

    This is the artifact that lets you reconstruct the routing (operation order)
    and find the join keys linking per-operation parameters to the final-QC
    result. For CiP-DMD the stations, parameters, and QC limits are documented
    in the dataset README / paper.
    """
    if dataset != "cip_dmd":
        raise NotImplementedError(f"map_schema not implemented for {dataset!r}")

    # Data dictionary based on the CiP-DMD paper and dataset README.
    # QC limits from data/raw/README.md "Quality control limits" table.
    entries = [
        # --- ID columns ---
        {"column": "part_id_cylinder_bottom", "station": "-",
         "parameter": "cylinder bottom part ID", "dtype": "id",
         "units": "-", "role": "id"},
        {"column": "part_id_piston_rod", "station": "-",
         "parameter": "piston rod part ID", "dtype": "id",
         "units": "-", "role": "id"},
        # --- Saw (Kasto SBA 2) ---
        {"column": "saw_weight", "station": "saw",
         "parameter": "weight after sawing", "dtype": "continuous",
         "units": "kg", "role": "quality",
         "lower_spec": 0.495, "upper_spec": 0.641},
        {"column": "saw_anomaly", "station": "saw",
         "parameter": "anomaly class (0=normal, 1=bad alignment)",
         "dtype": "categorical", "units": "-", "role": "process"},
        # --- CNC Milling (DMC 50H) ---
        {"column": "mill_surface_roughness", "station": "cnc_mill",
         "parameter": "surface roughness", "dtype": "continuous",
         "units": "µm Ra", "role": "quality",
         "lower_spec": 0.0, "upper_spec": 2.5},
        {"column": "mill_parallelism", "station": "cnc_mill",
         "parameter": "parallelism", "dtype": "continuous",
         "units": "mm", "role": "quality",
         "lower_spec": 0.0, "upper_spec": 0.1},
        {"column": "mill_groove_depth", "station": "cnc_mill",
         "parameter": "groove depth", "dtype": "continuous",
         "units": "mm", "role": "quality",
         "lower_spec": 0.75, "upper_spec": 0.85},
        {"column": "mill_groove_diameter", "station": "cnc_mill",
         "parameter": "groove diameter", "dtype": "continuous",
         "units": "mm (deviation from nominal)", "role": "quality",
         "lower_spec": 39.906, "upper_spec": 39.999},
        {"column": "mill_anomaly", "station": "cnc_mill",
         "parameter": "anomaly class (0=normal, 1=saw misalign, 2=clamp, 3=misc)",
         "dtype": "categorical", "units": "-", "role": "process"},
        # --- CNC Lathe (Index C65) ---
        {"column": "lathe_coaxiality", "station": "cnc_lathe",
         "parameter": "coaxiality", "dtype": "continuous",
         "units": "µm", "role": "quality",
         "lower_spec": 0.0, "upper_spec": 50.0},
        {"column": "lathe_diameter", "station": "cnc_lathe",
         "parameter": "diameter", "dtype": "continuous",
         "units": "mm (deviation from nominal)", "role": "quality",
         "lower_spec": -0.018, "upper_spec": 0.018},
        {"column": "lathe_length", "station": "cnc_lathe",
         "parameter": "length", "dtype": "continuous",
         "units": "mm", "role": "quality",
         "lower_spec": 163.45, "upper_spec": 163.75},
        # --- Assembly ---
        {"column": "assembly_rework", "station": "assembly",
         "parameter": "rework required", "dtype": "categorical",
         "units": "y/n", "role": "quality"},
        {"column": "assembly_pressure", "station": "assembly",
         "parameter": "pressure test", "dtype": "continuous",
         "units": "N", "role": "quality",
         "lower_spec": 7564.452, "upper_spec": 16486.026},
    ]

    data_dict = pd.DataFrame(entries)
    # Fill missing spec limits with NaN
    for col in ("lower_spec", "upper_spec"):
        if col not in data_dict.columns:
            data_dict[col] = pd.NA

    return data_dict
