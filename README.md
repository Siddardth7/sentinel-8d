# Sentinel-8D: Statistical Root-Cause Traceback & AIAG 8D Corrective Action

> Tracing final-inspection nonconformances across a multi-stage machining routing back to upstream station parameters via multivariate ANOVA and logistic regression ($p < 0.05$), closed with an audit-grade AIAG 8D report.

![status](https://img.shields.io/badge/status-planning-yellow)
![python](https://img.shields.io/badge/python-3.11-blue)
![data](https://img.shields.io/badge/dataset-CiP--DMD-informational)
![license](https://img.shields.io/badge/license-MIT-green)

**Codename:** `sentinel-8d`  
**Formal Case Study Title:** Statistical Root-Cause Traceback and AIAG 8D Corrective Action in Multi-Stage Discrete Manufacturing  
**Skill area:** Root-Cause Analysis · 8D / CAPA · MRB Disposition · Statistical Parameter Isolation  
**Domain:** Advanced Discrete Manufacturing (Cross-domain: Semiconductor, Aerospace, Automotive)  
**Headline deliverable:** A completed 8D Corrective Action Report whose root cause is proven with data, not guessed.

---

## The problem

In multi-step discrete manufacturing, a defect caught at final inspection is rarely caused by the *last* operation. The true cause usually lives several stations upstream — a drift in feed rate, a worn tool, an out-of-spec setpoint. Quality engineers have to trace the failure back through the routing to the exact station and parameter, then close it with a permanent corrective action. Do it by intuition and you fix the wrong step; do it with data and you close the loop for good.

## The dataset

**CiP-DMD** — *A new benchmark dataset for machine learning applications in discrete manufacturing* (TU Darmstadt, Center for industrial Productivity). 847 pneumatic cylinders through a multi-step machining process, with **named** process parameters and quality measurements linked by a traceability framework. License **CC-BY-4.0**. DOI [10.5281/zenodo.8420132](https://zenodo.org/records/8420132).

The named parameters are the whole point: they let the root cause be a concrete, defensible statement ("Operation 30 feed rate") instead of an anonymized feature index.

## Approach in three moves

1. **Reproduce an MRB quarantine** — filter to final-QC failures and treat them as a nonconformance to disposition.
2. **Trace upstream** — ANOVA / logistic regression correlating final pass-fail to each upstream parameter; isolate the offending station and parameter with p-values and effect sizes.
3. **Author the 8D** — D1–D8, with the data-backed root cause in D4 and an SPC-based permanent corrective action in D5–D7.

## Deliverables

- `reports/8D_Report.pdf` — the headline artifact (AIAG-format 8D).
- `notebooks/analysis.ipynb` — reproducible traceback analysis.
- `reports/figures/` — Pareto of defects, effect plots, the "smoking-gun" parameter chart.
- One quantified résumé bullet.

## Repository structure

```
sentinel-8d/
├── README.md            ← this file
├── roadmap.md           ← milestones & timeline
├── idea.md              ← full problem framing, solution, deliverables
├── execution.md         ← how it gets built, step by step
├── resources.md         ← datasets, papers, standards, tutorials, libraries
├── data/                ← raw + processed (git-ignored if large)
├── notebooks/           ← analysis
├── src/                 ← reusable functions
└── reports/             ← 8D report + figures
```

## Status

Planning. See [`roadmap.md`](roadmap.md) for the milestone checklist.

## Author

**Siddardth Pathipaka** — Quality & Process Engineer · M.S. Aerospace Engineering (UIUC) · Six Sigma Green Belt
GitHub: [@Siddardth7](https://github.com/Siddardth7)
