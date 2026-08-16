# Day 3 — Defect characterization & univariate screen (start)

**Goal:** establish the baseline (rate + volume), Pareto the failure modes and pick
the **one** to chase, then start testing every upstream parameter for a pass-vs-fail
difference.

**Time budget:** ~3–4 h (≈1.5 h characterization, ≈2 h screening setup).

**Covers:** `execution.md` §5–6 · **Milestone:** M2 start.

**Where you left off:** `data/processed/parts.parquet` exists with a `fail` column.

---

## 1. Load the tidy table

```python
import pandas as pd
parts = pd.read_parquet("../data/processed/parts.parquet")
parts.shape
```

## 2. Baseline numbers (these go verbatim into 8D-D2)

Compute and **print** (you'll copy the exact figures into the report later — but
only ones the notebook produced):
- total parts
- failure count
- overall defect rate (%)

## 3. Pareto → pick the dominant failure mode

If your data distinguishes *which characteristic* failed, build a **Pareto** of
failure modes and pick the single dominant one to chase (scope discipline —
`execution.md` §5 and the risk register both say: **one failure mode only**).

- Save `reports/figures/pareto.png`.
- If the label is a single pass/fail with no sub-modes (common on Bosch), your
  "dominant mode" is just the overall reject — say so explicitly and move on.

Then narrow `fail` to that mode (revisit `clean.define_label` if needed) and
re-save `parts.parquet`.

## 4. Frame the 5W2H problem description

From the baseline numbers, draft the **what / where / when / how many** for
`reports/8D_Report.md` **D2**. It's fine to write prose now and swap in exact
numbers later — just mark placeholders so nothing hand-typed sneaks through.

## 5. Start the univariate screen → implement `stats.univariate_screen`

Open `src/stats.py`. For each upstream parameter (use `role == "process"` from your
data dictionary to pick these), test whether it differs between pass and fail:

| Parameter type | Test | Report |
|----------------|------|--------|
| Continuous | Welch's t-test / one-way ANOVA | mean diff, t/F, **p**, **Cohen's d** |
| Categorical / setpoint | χ² test of independence | χ², **p**, **Cramér's V** |

`scipy.stats` has `ttest_ind(..., equal_var=False)`, `f_oneway`, `chi2_contingency`.

Return a DataFrame: one row per parameter with the statistic, raw p, and effect
size. You'll add the multiple-comparison correction and the shortlist tomorrow —
today, get the per-parameter tests running end to end.

---

## Tools today
- **pandas** — grouping, value counts, Pareto.
- **scipy.stats** — `ttest_ind`, `f_oneway`, `chi2_contingency`.
- **matplotlib / seaborn** — the Pareto chart.

## Hints & pitfalls
- **Effect size from the start.** Compute Cohen's d / Cramér's V *alongside* every
  p-value. Tomorrow's shortlist needs both; a tiny p on huge N is not a finding.
- **Welch, not Student.** Use `equal_var=False` — station parameters rarely have
  equal variance across pass/fail.
- **One mode only.** Resist chasing several failure modes; that's a documented
  stretch, not the base case (`execution.md` §13).
- Don't run the screen on ID or quality columns — only process parameters.

## Done checklist
- [ ] Baseline rate + failure count + total parts computed by the notebook.
- [ ] `reports/figures/pareto.png` saved; dominant failure mode chosen.
- [ ] `fail` reflects the chosen mode; `parts.parquet` re-saved if changed.
- [ ] D2 5W2H drafted (with placeholders for exact numbers).
- [ ] `stats.univariate_screen` runs and returns per-parameter p + effect size.

## What's next
→ [day-4.md](day-4.md): finish the screen (FDR/Bonferroni + shortlist), then start
the logistic model with a VIF check.
