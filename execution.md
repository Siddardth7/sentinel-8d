# Execution — Multi-Station Defect Traceback → 8D

*The minute-detail build plan: environment, data pipeline, the exact statistical methodology with decision rules, how each result maps into the 8D, a validation checklist, an hour-level schedule, and the pitfalls to avoid. Paired with `idea.md` (the why/what).*

---

## 1. Environment & tooling

**Language:** Python 3.11 in a dedicated virtual environment.

```bash
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install pandas numpy scipy statsmodels scikit-learn \
            matplotlib seaborn jupyter openpyxl pyarrow
pip freeze > requirements.txt
```

**Folder scaffolding (create on Day 1):**
```
multistation-rca-8d/
├── data/
│   ├── raw/                 # untouched download (git-ignored)
│   └── processed/           # tidy one-row-per-part table
├── notebooks/
│   └── 01_traceback.ipynb
├── src/
│   ├── load.py              # download + schema mapping
│   ├── clean.py            # tidy/join to one row per part
│   └── stats.py           # screening + logistic isolation helpers
├── reports/
│   ├── 8D_Report.md/.pdf
│   └── figures/
└── requirements.txt
```

**Library roles:** `pandas`/`numpy` (wrangling), `scipy.stats` (t-test/ANOVA/χ²), `statsmodels` (logistic regression, odds ratios, CIs, VIF), `scikit-learn` (gradient-boosted / random-forest cross-check + importances), `matplotlib`/`seaborn` (figures).

---

## 2. Step 0 — Data acquisition & access gate (Day 1, ~2 h)

1. Attempt the **preferred** dataset: retrieve CiP-DMD data files via the paper's data-availability route (see `resources.md`). **Hard gate:** if usable CSVs aren't in hand within ~1 hour, switch to the committed fallback.
2. **Fallback:** download **Bosch Production Line Performance** from Kaggle (`train_numeric.csv` etc.). It's large (~2 GB numeric); work on a **stratified sample** (keep all failures + a matched sample of passes) so iteration stays fast.
3. Record which dataset was used, its version/date, and the download URL in the notebook header and README.

*Decision rule:* the rest of the pipeline is dataset-agnostic — only column names and the failure-label definition differ.

---

## 3. Step 1 — Data understanding & process map (Day 1–2, ~3 h)

- Build a **data dictionary**: for every column, record {station/operation, parameter name, type (continuous/categorical), units, role (process vs. quality vs. ID)}.
- Reconstruct the **routing** (operation order). For Bosch, station order is encoded in the feature naming (Line→Station→Feature); for CiP-DMD, it's documented.
- Identify the **join keys** linking each part's per-operation parameters to its final-QC result.
- Deliverable of this step: a one-page process-flow sketch saved to `reports/figures/process_flow.png`.

---

## 4. Step 2 — Cleaning & tidying (Day 2, ~3 h)

- **Reshape** to **one row per part**: columns = each upstream parameter; plus the final-QC outcome. (Bosch is already wide; CiP-DMD may need a pivot from long form.)
- **Missing values:** quantify per column. Drop columns with excessive missingness; for the rest, note that missingness itself may be informative (a station not visited) — encode a missing-indicator rather than blindly imputing.
- **Types & units:** enforce numeric dtypes; standardize units; strip constant/zero-variance columns.
- **Target:** define the binary label `fail` (1 = final-QC reject on the characteristic of interest). Save `data/processed/parts.parquet`.

---

## 5. Step 3 — Defect characterization (D2 evidence) (Day 3, ~2 h)

- **Baseline:** overall defect rate, failure count, total parts (these numbers go verbatim into 8D-D2).
- **Pareto** of failure modes / failing characteristics → pick the **single dominant mode** to chase. Save `reports/figures/pareto.png`.
- Frame the **5W2H** problem description (what/where/when/how many) from these numbers.

---

## 6. Step 4 — Univariate screening (Day 3–4, ~3 h)

For each upstream parameter, test whether it differs between `pass` and `fail`:

| Parameter type | Test | Statistic reported |
|----------------|------|--------------------|
| Continuous | Welch's t-test (unequal variance) / one-way ANOVA | mean diff, t/F, p, Cohen's d |
| Categorical / setpoint | χ² test of independence | χ², p, Cramér's V |

**Decision rules:**
- Control the false-discovery rate across the many tests with **Benjamini–Hochberg (FDR)**; report **Bonferroni** as the stricter cross-check.
- Keep a **shortlist** of parameters passing the corrected threshold *and* showing a non-trivial effect size (small p on a huge N is not enough — require d ≥ ~0.2 or a meaningful Cramér's V).
- Save an effect-ranking table to `reports/figures/univariate_ranking.png`.

---

## 7. Step 5 — Multivariate isolation (D4 evidence) (Day 4–5, ~4 h)

**Model:** logistic regression `fail ~ shortlisted parameters (+ station controls)` via `statsmodels`.

**Pre-model hygiene:**
- **Standardize** continuous predictors (z-score) so coefficients are comparable.
- **Multicollinearity:** compute **VIF**; if VIF > ~5, drop or combine correlated parameters (they'd otherwise split the credit and hide the true driver).
- **Class imbalance:** fit with class weights; if failures are very rare, also fit a penalized (L2 / Firth-style) model to stabilize estimates.

**Read-out:**
- **Odds ratios** with 95% CIs and p-values → the parameter with the largest, most significant, CI-excluding-1 effect is the prime suspect.
- **Cross-check:** fit a gradient-boosted / random-forest classifier; compare its **feature importances** (and a SHAP or permutation-importance view) to the logistic result. **Require agreement** on the top driver before concluding — this guards against a model-specific artifact.

---

## 8. Step 6 — Root-cause confirmation & escape point (Day 5–6, ~3 h)

- **State the root cause** precisely: *Operation X, parameter Y, in condition Z (e.g., feed above threshold)*, with odds ratio, CI, and p.
- **Physics sanity check:** does the sign/direction match machining reality? (e.g., higher feed → rougher surface / oversize). If it contradicts physics, treat it as suspected confounding and revisit Step 5 before finalizing.
- **Escape point:** identify why the defect wasn't caught earlier — the offending step lacked an in-line control/gate. This becomes the target of the corrective action.
- **Quantify the prize:** estimate the defect-rate reduction if the driver is held in control (e.g., "holding parameter Y within ±σ removes the condition present in N% of failures").

---

## 9. Step 7 — Corrective-action design (Day 6, ~2 h)

- **Permanent corrective action:** place an **SPC control at the offending operation** — specify the chart (e.g., I-MR or X̄-R on parameter Y), the control limits (from the in-control subset), and the reaction plan.
- **Verification logic (D6):** show the expected effect (the failures concentrated in the out-of-control region; controlling it removes them).
- **Prevent recurrence (D7):** update the Control Plan and PFMEA at that station — this is the explicit hand-off to **Project 2**.

---

## 10. Step 8 — Author the 8D (Day 7–8, ~4 h)

Populate each discipline; every number traces to a notebook cell:

| Discipline | Content | Source step |
|------------|---------|-------------|
| D0 | Symptom / emergency response (containment trigger) | Step 3 |
| D1 | Cross-functional team & roles (framed) | — |
| D2 | Problem description (5W2H + baseline rate/volume) | Step 3 |
| D3 | Interim containment (100% inspection / lot quarantine) | — |
| D4 | Root cause + escape point (statistics) | Steps 4–6 |
| D5 | Permanent corrective action (SPC control + setpoint) | Step 7 |
| D6 | Validate the corrective action (expected reduction) | Steps 6–7 |
| D7 | Prevent recurrence (Control Plan / PFMEA update) | Step 7 → Project 2 |
| D8 | Closure & team recognition; archive evidence | — |

Render `reports/8D_Report.md` → PDF.

---

## 11. Validation & reproducibility checklist

- [ ] Fresh clone + `pip install -r requirements.txt` + run notebook top-to-bottom reproduces every figure and number.
- [ ] No hard-coded statistics in the 8D — all pulled from notebook outputs.
- [ ] Univariate screen uses FDR/Bonferroni correction (documented).
- [ ] Multivariate model reports odds ratios **with CIs**, not just point estimates.
- [ ] Logistic and tree-based models agree on the top driver.
- [ ] Root cause passes the physics sanity check.
- [ ] Dataset name, version, and URL recorded in README + notebook header.

---

## 12. Detailed schedule (1–2 weeks, part-time)

| Day | Focus | Output |
|-----|-------|--------|
| 1 | Env setup; data access gate; scaffolding | working repo, dataset in `data/raw/` |
| 2 | Data dictionary; process map; tidy to one-row-per-part | `parts.parquet`, process-flow figure |
| 3 | Defect characterization; start univariate screen | Pareto, baseline numbers |
| 4 | Finish univariate; begin logistic model | ranked parameters, first model |
| 5 | Multivariate isolation + tree cross-check | odds ratios, importances, top driver |
| 6 | Root-cause confirmation; corrective-action design | root-cause statement, SPC spec |
| 7 | Draft 8D (D0–D8) | `8D_Report.md` |
| 8 | Render PDF; clean notebook; figures | `8D_Report.pdf` |
| 9 | README summary + résumé bullet; final review | portfolio-ready outcome |
| 10 | Buffer / stretch (SPC-at-station chart; Bosch scale-check) | optional extras |

---

## 13. Pitfalls & how to avoid them

- **P-hacking with many columns** → always apply multiple-comparison correction; lead with effect size, not just p.
- **Blaming a correlated bystander** → VIF + multivariate model + require model agreement.
- **Imbalance instability** → class weights / penalized fit; report CIs.
- **Story over evidence** → the physics sanity check is a hard gate, not a formality.
- **Irreproducible numbers** → generate every 8D figure from the notebook; never paste a value you can't regenerate.
- **Scope creep** → one dominant failure mode only; extra failures are a documented stretch.

## 14. Definition of done

A rendered 8D PDF whose D4 names a specific station+parameter (effect size, CI, p < 0.05, model agreement, physics-consistent) and whose D5–D7 specify a concrete SPC control and PFMEA/Control-Plan update — plus a one-command-reproducible notebook and a README outcome summary. Then: publish to GitHub, tag `v1.0`.
