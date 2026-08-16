"""Stage 1 — data acquisition & schema mapping.

Covers execution.md §2 (Step 0) and the first half of §3 (Step 1).
You implement these on Day 1 (acquisition) and Day 2 (schema/dictionary).

Design goal: everything downstream is *dataset-agnostic*. Only this module knows
whether we are on the preferred CiP-DMD data or the Bosch fallback — it returns a
raw DataFrame plus a data dictionary, and the rest of the pipeline works on those.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# Project-root-relative paths. src/ is one level below the repo root.
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def load_raw(dataset: str) -> pd.DataFrame:
    """Read the untouched download from data/raw/ into a DataFrame.

    Parameters
    ----------
    dataset : {"cip_dmd", "bosch"}
        Which source is in hand. Set on Day 1 by the data access gate.

    Returns
    -------
    pandas.DataFrame
        The raw table(s). For Bosch, work on a *stratified sample* (keep all
        failures + a matched sample of passes) — see execution.md §2 — so
        iteration stays fast; do the sampling here, not downstream.

    TODO(day-1/2):
      - CiP-DMD: locate the actual CSV/XLSX files (the Zenodo record is the PAPER
        only; data routes through the InterQ project — see resources.md §1).
      - Bosch: read train_numeric.csv; this is ~2 GB, so read in chunks or with
        usecols, and down-sample immediately.
      - Record dataset name + version/date + download URL for the notebook header
        and README (execution.md §2 step 3).
    """
    raise NotImplementedError("Implement on Day 1 — see guides/day-1.md")


def map_schema(df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    """Build the data dictionary: one row per column of `df`.

    Columns of the returned frame:
        column, station, parameter, dtype (continuous/categorical),
        units, role (id | process | quality)

    This is the artifact that lets you reconstruct the routing (operation order)
    and find the join keys linking per-operation parameters to the final-QC
    result. For Bosch the station order is encoded in the feature naming
    (Line -> Station -> Feature); for CiP-DMD it is documented in the paper.

    TODO(day-2): parse column names into (station, parameter); classify role;
    save the dictionary alongside the notebook so it's reviewable.
    """
    raise NotImplementedError("Implement on Day 2 — see guides/day-2.md")
