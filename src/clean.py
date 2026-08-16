"""Stage 2 — cleaning & tidying to one row per part.

Covers execution.md §4 (Step 2). You implement this on Day 2.

Output contract: a tidy frame with one row per finished part, one column per
upstream parameter, plus a single binary `fail` column. Persisted to
data/processed/parts.parquet so later stages never re-parse raw data.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"


def tidy_one_row_per_part(raw: pd.DataFrame, data_dict: pd.DataFrame) -> pd.DataFrame:
    """Reshape raw data into one row per part.

    Bosch is already wide (one row per part). CiP-DMD may be long (one row per
    operation) and need a pivot keyed on the part ID from the traceability keys
    identified in load.map_schema().

    TODO(day-2):
      - join / pivot process rows to quality rows on the part key
      - enforce numeric dtypes; standardize units; drop constant / zero-variance
        columns (they carry no signal and break VIF later)
    """
    raise NotImplementedError("Implement on Day 2 — see guides/day-2.md")


def handle_missing(df: pd.DataFrame, max_missing_frac: float = 0.5) -> pd.DataFrame:
    """Quantify and handle missing values.

    Rule of thumb (execution.md §4): drop columns above `max_missing_frac`
    missing. For the rest, DO NOT blindly impute — missingness can be
    informative (a station a part never visited). Prefer adding a
    `<col>_missing` indicator column over silent imputation.

    TODO(day-2): report per-column missingness before acting; add indicators.
    """
    raise NotImplementedError("Implement on Day 2 — see guides/day-2.md")


def define_label(df: pd.DataFrame) -> pd.DataFrame:
    """Add the binary target `fail` (1 = final-QC reject on the mode of interest).

    The specific failing characteristic to chase is chosen on Day 3 from the
    Pareto (execution.md §5). Until then this may just encode the raw pass/fail
    (e.g. Bosch `Response`).

    TODO(day-2/3): define `fail`; sanity-check its rate against the known
    baseline; this rate/volume goes verbatim into 8D-D2.
    """
    raise NotImplementedError("Implement on Day 2/3 — see guides/day-2.md")


def save_processed(df: pd.DataFrame, name: str = "parts.parquet") -> Path:
    """Write the tidy table to data/processed/ and return its path."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = PROCESSED_DIR / name
    df.to_parquet(out, index=False)
    return out
