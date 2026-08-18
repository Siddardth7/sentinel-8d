# Sentinel-8D: Statistical Root-Cause Traceback & AIAG 8D Corrective Action

> Tracing final-inspection nonconformances across a multi-stage discrete manufacturing routing back to upstream station parameters via multivariate ANOVA, Welch's $t$-tests, and logistic regression ($p < 0.05$), closed with an audit-grade AIAG 8D report.

![status](https://img.shields.io/badge/status-complete-brightgreen)
![python](https://img.shields.io/badge/python-3.11-blue)
![data](https://img.shields.io/badge/dataset-CiP--DMD-informational)
![license](https://img.shields.io/badge/license-MIT-green)

**Codename:** `sentinel-8d`  
**Formal Case Study Title:** Statistical Root-Cause Traceback and AIAG 8D Corrective Action in Multi-Stage Discrete Manufacturing  
**Skill area:** Root-Cause Analysis · AIAG 8D / CAPA · MRB Disposition · Statistical Parameter Isolation · SPC · PFMEA  
**Domain:** Advanced Discrete Manufacturing (Cross-domain: Semiconductor, Aerospace, Automotive)  
**Headline deliverable:** A complete, audit-grade 8D Corrective Action Report whose root cause is proven with multi-model statistical consensus, not guessed.

---

## Executive Results Summary

| Project Milestone | Metric / Finding | Engineering Implication |
|:---|:---|:---|
| **Baseline Non-Conformance (D2)** | **$52$ defects / $802$ assembled cylinders** = **$6.48\%$ failure rate** ($64,838$ DPMO) | High rework cost and assembly line teardown risk flagged at end-of-line functional acceptance. |
| **Multicollinearity Diagnostic** | All Variance Inflation Factors ($\text{VIF}$) $\in [1.02, 1.09] \ll 5.0$ | Predictor isolation is clean and free of collinear bystander confounding. |
| **Statistical Root Cause (D4)** | **Operation 10: Sawing Station (Kasto SBA 2)** $\rightarrow$ **`saw_weight` deficit** ($< 0.540$ kg) | Each $1\sigma$ decrease in cut blank weight nearly doubles failure odds: $\mathbf{\text{OR} = 0.503}$ ($95\%\text{ CI: } [0.371, 0.683], \mathbf{p = 1.00 \times 10^{-5}}$). |
| **Multi-Model Consensus** | Logistic Regression, Random Forest ($\Delta\text{AUC}=0.071$), Gradient Boosting ($\Delta\text{AUC}=0.058$) | Unanimous #1 driver ranking across independent linear and tree-based model families. |
| **Engineering Physics Gate** | Undersized saw blanks slip in CNC milling fixture $\rightarrow$ face non-parallelism $\rightarrow$ stroke binding | **Passed**. Statistical sign ($\beta = -0.687$) aligns with machining and hydraulic clamping mechanics. |
| **Escape Point** | Sawing station lacked in-line checkweigher or length stop | Allowed short blanks to escape undetected into downstream CNC Milling and Assembly. |
| **Permanent Corrective Action (D5)** | **I-MR Statistical Process Control Chart** on `saw_weight` with 4-step OCAP | Control limits from in-control subset ($N=750$): $\bar{X} = 0.5685$ kg, $\text{LCL} = 0.5307$ kg, $\text{UCL} = 0.6063$ kg. |
| **Validated Defect Reduction (D6)** | **$36.5\%$ of all assembly rework defects prevented** ($19/52$ failures eliminated) | Plant defect rate drops from $6.48\%$ ($64,838$ DPMO) to $4.85\%$ ($48,529$ DPMO). |
| **Risk Reduction & Hand-Off (D7)** | Control Plan `CP-CYL-OP10-REV2` & PFMEA `PFMEA-CYL-OP10-REV2` RPN: $\mathbf{336} \rightarrow \mathbf{28}$ | **$-91.7\%$ RPN reduction** ($S=7, O=6\rightarrow 2, D=8\rightarrow 2$); formal hand-off to **Project 2**. |

---

## Quantified Portfolio Résumé Bullet

> **"Isolated the physical root cause of end-of-line functional failures across an 802-part multi-station manufacturing dataset to an upstream saw cut mass deficit using Welch's t-tests, FDR-corrected univariate screening, and multivariate logistic regression ($\text{OR} = 0.503, p = 1.00 \times 10^{-5}$); validated consensus across Random Forest and Gradient Boosting models, and authored an AIAG-format 8D report implementing an in-line I-MR SPC control that prevents $36.5\%$ of assembly rework defects and reduces PFMEA RPN by $91.7\%$ ($336 \rightarrow 28$)."**

---

## The Problem & Engineering Context

In multi-step discrete manufacturing, a defect caught at final functional inspection is rarely caused by the *last* operation. The true root cause usually lives several stations upstream — a drift in feed rate, a worn tool, an out-of-spec setpoint, or feed stock misalignment. Quality engineers must trace the failure back through the routing to the exact station and parameter, prove the mechanism with data, and close the loop with an institutionalized Statistical Process Control (SPC) corrective action.

## The Dataset

**CiP-DMD** — *Discrete Manufacturing Dataset* (TU Darmstadt, Center for Industrial Productivity). 802 assembled pneumatic cylinders tracked through sawing, CNC milling, and CNC lathe operations, with **named** engineering parameters and physical quality measurements linked by a component-level traceability framework. License **CC-BY-4.0**. DOI [10.5281/zenodo.8420132](https://zenodo.org/records/8420132).

---

## End-to-End Analysis Architecture

```
                       CiP-DMD Manufacturing Routing
                       =============================
                       
  Cylinder Bottom:  [Raw Bar Stock] -> [Saw Station (Kasto SBA 2)] -> [CNC Milling (DMC 50H)] --\
                                            ^                                                    \
                                     (Root Cause Escape)                                          \---> [Assembly & QC]
                                                                                                 /      (Rework Target)
  Piston Rod:       [Raw Rod Stock] ----------------> [CNC Lathe (Index C65)] ------------------/
```

1. **Step 0–2 (Data Pipeline & Tidy Table)**: Ingest raw multi-table CSVs and metadata JSONs, map data dictionary, handle missingness with indicator columns, and assemble the 802-part tidy dataset (`data/processed/parts.parquet`).
2. **Step 3 (Defect Characterization & 8D-D2)**: Compute baseline metrics ($6.48\%$ rework rate) and generate defect Pareto chart (`reports/figures/pareto.png`).
3. **Step 4 (Univariate Screening & Ranking)**: Execute Welch's $t$-tests and $\chi^2$ independence tests under Benjamini–Hochberg False Discovery Rate control (`reports/figures/univariate_ranking.png`).
4. **Step 5 (Multivariate Isolation & Tree Cross-Check)**: Verify multicollinearity via VIF ($< 1.09$), fit standardized multivariate logistic regression ($\text{OR} = 0.503, p = 1.00 \times 10^{-5}$), and confirm model consensus via Random Forest / Gradient Boosting permutation importance.
5. **Step 6 (Root Cause Confirmation & The Prize)**: Validate physical mechanism, identify escape point, quantify defect reduction prize ($36.5\%$), and generate smoking-gun figure (`reports/figures/smoking_gun.png`).
6. **Step 7 (SPC Corrective Action & 8D-D5/D8)**: Establish in-line I-MR control chart (`reports/figures/spc_chart.png`), define 4-step OCAP reaction plan, and author complete AIAG 8D report (`reports/8D_Report.md` / `reports/8D_Report.html`).

---

## Deliverables & Artifacts

- **Headline 8D Report**: [`reports/8D_Report.md`](reports/8D_Report.md) & Standalone Styled [`reports/8D_Report.html`](reports/8D_Report.html)
- **Traceback Analysis Notebook**: [`notebooks/01_traceback.ipynb`](notebooks/01_traceback.ipynb) (100% reproducible top-to-bottom)
- **Statistical Evidence Figures**:
  - `reports/figures/process_flow.png` — Multi-station manufacturing routing & QC limits
  - `reports/figures/pareto.png` — Line-wide defect Pareto distribution
  - `reports/figures/univariate_ranking.png` — FDR-corrected univariate effect size ranking
  - `reports/figures/smoking_gun.png` — Distribution separation & defect surge in short blanks
  - `reports/figures/spc_chart.png` — I-MR SPC control chart with in-control 3-sigma limits
- **Modular Python Source Engine**:
  - `src/load.py` — Raw data ingestion & schema mapping
  - `src/clean.py` — Traceability join, missing value handling & labeling
  - `src/stats.py` — Screening, VIF, logistic regression, tree cross-check

---

## Repository Structure

```
sentinel-8d/
├── README.md                     # this file
├── requirements.txt              # pinned Python dependencies
├── notebooks/
│   └── 01_traceback.ipynb        # end-to-end reproducible analysis (raw → 8D)
├── src/                          # modular, dataset-agnostic analysis engine
│   ├── load.py                   # raw ingestion & schema mapping
│   ├── clean.py                  # traceability join, missing-value handling, labeling
│   └── stats.py                  # screening, VIF, logistic regression, tree cross-check
├── scripts/                      # standalone figure + report generators
│   ├── fetch_cip_dmd.py          # selective dataset download (resumable)
│   ├── gen_*.py                  # one script per statistical figure
│   └── render_report_html.py     # compiles 8D_Report.md → standalone HTML
├── reports/
│   ├── 8D_Report.md / .html      # headline deliverable (AIAG 8D, D0–D8)
│   └── figures/*.png             # statistical evidence figures
└── data/                         # raw/ + processed/ (contents git-ignored)
```

## Reproduce

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. Fetch the CiP-DMD source data (resumable; skip if you already have data/raw/)
python scripts/fetch_cip_dmd.py

# 2. Run the analysis end-to-end (writes data/processed/parts.parquet)
jupyter nbconvert --to notebook --execute --inplace notebooks/01_traceback.ipynb

# 3. Regenerate every figure and re-render the 8D report
python scripts/gen_process_flow.py
python scripts/gen_pareto.py
python scripts/gen_univariate_ranking.py
python scripts/gen_smoking_gun.py
python scripts/gen_spc_chart.py
python scripts/render_report_html.py
```

Figures in steps 2–5 read directly from `data/processed/parts.parquet`, so every
number in the report and charts traces back to the raw dataset.

---

## Roadmap & Future Work

The 8D corrective-action cycle (D0–D8) is **complete**: root cause proven with
multi-model statistical consensus, permanent I-MR SPC control installed, and the
control plan / PFMEA handed off. The directions below extend the case study from
a retrospective, single-parameter traceback toward a live, plant-wide predictive
quality system — each one a natural next station on the same dataset.

- **Predictive / multivariate SPC.** Replace the univariate I-MR chart with a
  Hotelling $T^2$ / MEWMA monitor over the full station-parameter vector, so
  combinations that are each in-spec but jointly defect-precursive are caught
  before a part fails — shifting from *detection* to *forecasting* defect
  probability hours ahead.
- **Probabilistic root cause across the routing.** Fit a Bayesian network over
  the traceability graph to reason about *interacting* multi-station causes and
  attach calibrated probabilities to each candidate, rather than isolating one
  dominant parameter at a time.
- **Explainable model consensus.** Layer SHAP attribution on the existing Random
  Forest / Gradient Boosting cross-check to turn "unanimous #1 driver" into
  per-part, auditor-readable explanations.
- **Tool-wear survival modeling.** Treat feed-rate and blank-mass drift as a
  time-to-failure process (Cox / Weibull) to predict *when* the saw station
  crosses the escape threshold, enabling condition-based maintenance instead of
  fixed intervals.
- **Streaming deployment / digital twin.** Wire the `src/` engine to live station
  telemetry for real-time traceback and an in-line checkweigher feedback loop,
  closing the escape point identified in D4 at the source.

---

## Author

**Siddardth Pathipaka** — Quality & Process Engineer · M.S. Aerospace Engineering (UIUC) · Six Sigma Green Belt  
GitHub: [@Siddardth7](https://github.com/Siddardth7)
