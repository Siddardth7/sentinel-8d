# Sprint guides — how to build Sentinel-8D in 7 days

These are your **step-by-step working guides**. The planning docs at the repo root
(`idea.md`, `execution.md`, `roadmap.md`, `resources.md`) explain the *why* and the
*full method*; these guides tell you *what to do each day, where, and with which
tools* — plus hints and the traps to avoid.

Plan for **~3–4 hours per day**. If a day runs long, the checklist at the bottom of
each guide tells you the minimum that must be done before moving on.

## How to use a guide

1. Open that day's file (e.g. `guides/day-1.md`).
2. Work top to bottom. Commands are copy-pasteable; file paths tell you where the
   work lands.
3. When a step says *"implement `stats.univariate_screen`"*, open the matching stub
   in `src/` — it already has the signature, docstring, and a `TODO` describing
   exactly what to build.
4. Tick the **Done checklist** before moving to the next day.
5. Stuck? That's the point of doing this with an assistant — ask for help on the
   specific step.

## The 7-day map

This compresses the 10-day schedule in `execution.md` §12 into 7 working days.

| Day | Guide | Focus | execution.md |
|-----|-------|-------|--------------|
| 1 | [day-1.md](day-1.md) | Environment, repo scaffold, **data access gate** | §1–2 |
| 2 | [day-2.md](day-2.md) | Data dictionary, process map, tidy → `parts.parquet` | §3–4 |
| 3 | [day-3.md](day-3.md) | Defect Pareto + baseline, start univariate screen | §5–6 |
| 4 | [day-4.md](day-4.md) | Finish univariate, begin logistic model + VIF | §6–7 |
| 5 | [day-5.md](day-5.md) | Multivariate isolation, tree cross-check, root cause | §7–8 |
| 6 | [day-6.md](day-6.md) | SPC corrective action, draft the 8D (D0–D8) | §9–10 |
| 7 | [day-7.md](day-7.md) | Render PDF, clean notebook, README bullet, tag v1.0 | §10, §12 |

## Where you'll be working

```
sentinel-8d/
├── src/            ← reusable functions you implement (load, clean, stats)
├── notebooks/      ← 01_traceback.ipynb: the analysis, run top-to-bottom
├── data/raw/       ← your download (git-ignored)
├── data/processed/ ← parts.parquet (you generate it Day 2)
└── reports/        ← 8D_Report.md + figures/
```

The golden rule (from `execution.md` §11): **no hand-typed statistics in the 8D.**
Every number and figure is produced by the notebook. If you can't regenerate it,
it doesn't go in the report.
