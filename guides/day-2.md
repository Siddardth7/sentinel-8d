# Day 2 — Data dictionary, process map & tidy table

**Goal:** understand the columns, reconstruct the routing (operation order), and
produce **one tidy row per part** saved to `data/processed/parts.parquet`.

**Time budget:** ~3–4 h (≈1.5 h dictionary + process map, ≈2 h tidy/clean).

**Covers:** `execution.md` §3–4 · **Milestone:** M1 finish.

**Where you left off:** raw data in `data/raw/`, `DATASET` set in the notebook.

---

## 1. Build the data dictionary → implement `load.map_schema`

Open `src/load.py`. Implement `map_schema(df, dataset)` to return one row per
column with: `column, station, parameter, dtype (continuous/categorical), units,
role (id | process | quality)`.

- **Bosch:** parse names `L{line}_S{station}_F{feature}` to recover station order.
- **CiP-DMD:** the paper documents stations, parameters, and units — transcribe.

Then in the notebook (Step 0–1 section):

```python
raw = load.load_raw(DATASET)          # you implement this too (see below)
data_dict = load.map_schema(raw, DATASET)
data_dict.head(20)
```

You'll also need to flesh out `load.load_raw` — read the files from `data/raw/`,
and for Bosch **down-sample here** (all failures + matched passes).

## 2. Reconstruct the routing & find the join keys

- Establish the **operation order** (which station runs first, second, …).
- Identify the **join key(s)** that link each part's per-operation parameters to its
  final-QC result. For Bosch it's the part `Id`; for CiP-DMD it's the traceability
  key named in the paper.
- Save a one-page **process-flow sketch** to `reports/figures/process_flow.png`.
  A simple boxes-and-arrows diagram is fine — draw it in code (matplotlib) or by
  hand and photograph it; the point is to show you understand the line.

## 3. Tidy to one row per part → implement `clean.tidy_one_row_per_part`

Open `src/clean.py`. Contract: **columns = each upstream parameter; plus the
final-QC outcome; one row per finished part.**

- Bosch is already wide (one row per part) — mostly a column-selection job.
- CiP-DMD may be long (one row per operation) — pivot on the part key.
- Enforce numeric dtypes, standardize units, and **drop constant / zero-variance
  columns** (they carry no signal and will break VIF on Day 4).

## 4. Handle missing values → implement `clean.handle_missing`

- Quantify missingness **per column** first (print it — don't act blind).
- Drop columns above ~50% missing.
- For the rest, **don't blindly impute.** In multi-station data a missing value
  often means *"this part never visited that station"* — that's informative. Add a
  `<col>_missing` indicator instead of filling.

## 5. Define the label (first pass) → `clean.define_label`

Add binary `fail` (1 = final-QC reject). For Bosch that's `Response == 1`. The
*specific* failing characteristic to chase gets chosen tomorrow from the Pareto —
today just get a working `fail` and check its rate looks sane.

## 6. Save the processed table

```python
parts = clean.tidy_one_row_per_part(raw, data_dict)
parts = clean.handle_missing(parts)
parts = clean.define_label(parts)
path = clean.save_processed(parts)          # writes data/processed/parts.parquet
print(parts.shape, "->", path)
```

From Day 3 on, you load `parts.parquet` and never re-parse raw data.

---

## Tools today
- **pandas** — reshape, join/pivot, dtype enforcement, missingness counts.
- **pyarrow** — parquet write (via `df.to_parquet`, already wired in `save_processed`).
- **matplotlib** (optional) — the process-flow sketch.

## Hints & pitfalls
- **Parquet, not CSV**, for `parts` — it preserves dtypes and is fast. That's why
  `pyarrow` is in requirements.
- **Zero-variance columns bite later.** Drop them now; VIF and logistic regression
  choke on constants.
- **Missingness is a feature, not a nuisance.** The indicator-column trick can
  itself reveal a station-skip pattern that matters to root cause.
- Keep `map_schema` output around — you'll use `role` and `station` to pick which
  columns are "upstream parameters" (screen these) vs. IDs/quality (don't).

## Done checklist
- [ ] `load.map_schema` returns a data dictionary; you can see station/parameter/role.
- [ ] Routing (operation order) reconstructed; join key identified.
- [ ] `reports/figures/process_flow.png` saved.
- [ ] `data/processed/parts.parquet` written — one row per part, numeric, no
      constant columns.
- [ ] `fail` exists and its rate looks plausible.

## What's next
→ [day-3.md](day-3.md): characterize the defect (baseline + Pareto), pick the one
failure mode to chase, and start the univariate screen.
