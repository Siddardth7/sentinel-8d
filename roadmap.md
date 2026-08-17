# Roadmap — Multi-Station Defect Traceback → 8D

**Target duration:** 1–2 weeks (part-time) · **Definition of done:** a signed-off 8D report with a statistically proven root cause and a reproducible notebook.

---

## Milestones

### M1 — Data & problem framing (Days 1–2) — [COMPLETED]
- [x] Download CiP-DMD from Zenodo; locate the actual CSVs (via the *Data in Brief* supplement, not just the landing-page PDF).
- [x] Build a data dictionary: stations, operations, parameters, and the final-QC result column (`src/load.py`).
- [x] Map the process flow (station order) and confirm the traceability keys that link process rows to quality rows (`reports/figures/process_flow.png`).
- [x] Define the "MRB event": assembly rework requirement (`assembly_rework == 'y'`, 52 failures / 802 parts = 6.48%).

### M2 — Statistical traceback (Days 3–5) — [COMPLETED]
- [x] Compute a Pareto of defect modes; pick the dominant failure to chase (`reports/figures/pareto.png`).
- [x] Univariate screen: Welch's t-tests / ANOVA / Chi-Square under FDR control (`reports/figures/univariate_ranking.png`).
- [x] Multivariate model: logistic regression with standardized odds ratios and 95% CIs + VIF multicollinearity diagnostic.
- [x] Independent machine learning tree cross-check: Random Forest & Gradient Tree Boosting with ROC-AUC permutation importance.
- [x] Isolate the offending **station + parameter** (`saw_weight` at Sawing station, $\text{OR}=0.503, p=1.00 \times 10^{-5}$); sanity-check against the process physics.

### M3 — 8D authoring (Days 6–8) — [COMPLETED]
- [x] D0 symptom & emergency response / D1 team / D2 problem description (5W2H) / D3 interim containment.
- [x] D4 root cause + escape point (multi-model statistical evidence).
- [x] D5 permanent corrective action: I-MR SPC control on `saw_weight` with in-control 3-sigma limits ($\bar{X}=0.5685$ kg, $\text{LCL}=0.5307$ kg, $\text{UCL}=0.6063$ kg) + 4-step OCAP.
- [x] D6 validate: historical defect reduction of $36.5\%$ ($19/52$ failures prevented).
- [x] D7 prevent recurrence: Control Plan `CP-CYL-OP10-REV2` + PFMEA RPN reduction from $336 \rightarrow 28$ ($-91.7\%$), hand-off to Project 2.
- [x] D8 closure & team recognition.
- [x] Render the 8D report to standalone styled HTML with print-to-PDF CSS (`reports/8D_Report.html`).

### M4 — Package & publish (Days 9–10) — [COMPLETED]
- [x] Clean the notebook; verify 100% reproducible top-to-bottom execution.
- [x] Write the README result summary + quantified résumé bullet.
- [x] Push to GitHub; tag `v1.0`.

---

## Progress

| Milestone | Status |
|:---|:---:|
| **M1 Data & framing** | ✅ Complete |
| **M2 Statistical traceback** | ✅ Complete |
| **M3 8D authoring** | ✅ Complete |
| **M4 Package & publish** | ✅ Complete |

## Stretch Goals
- [x] Add an SPC chart at the offending station showing the out-of-control signal that predicts the final defect (`reports/figures/spc_chart.png`).
- [x] Full HTML report generation with embedded figure gallery and print styles.
