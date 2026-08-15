# Roadmap — Multi-Station Defect Traceback → 8D

**Target duration:** 1–2 weeks (part-time) · **Definition of done:** a signed-off 8D report with a statistically proven root cause and a reproducible notebook.

---

## Milestones

### M1 — Data & problem framing (Days 1–2)
- [ ] Download CiP-DMD from Zenodo; locate the actual CSVs (via the *Data in Brief* supplement, not just the landing-page PDF).
- [ ] Build a data dictionary: stations, operations, parameters, and the final-QC result column.
- [ ] Map the process flow (station order) and confirm the traceability keys that link process rows to quality rows.
- [ ] Define the "MRB event": which final-QC characteristic is the failure of interest.

### M2 — Statistical traceback (Days 3–5)
- [ ] Compute a Pareto of defect modes; pick the dominant failure to chase.
- [ ] Univariate screen: ANOVA / t-tests of each upstream parameter vs. pass/fail.
- [ ] Multivariate model: logistic regression (or classification) with parameter importance.
- [ ] Isolate the offending **station + parameter**; report effect size and p-value; sanity-check against the process physics.

### M3 — 8D authoring (Days 6–8)
- [ ] D1 team / D2 problem description (5W2H) / D3 interim containment.
- [ ] D4 root cause + escape point (the data result goes here).
- [ ] D5 permanent corrective action (e.g., SPC at the offending step) / D6 validate / D7 prevent recurrence / D8 closure.
- [ ] Render the 8D to PDF.

### M4 — Package & publish (Days 9–10)
- [ ] Clean the notebook; export final figures.
- [ ] Write the README result summary + one résumé bullet.
- [ ] Push to GitHub; tag `v1.0`.

---

## Progress

| Milestone | Status |
|-----------|--------|
| M1 Data & framing | ☐ Not started |
| M2 Statistical traceback | ☐ Not started |
| M3 8D authoring | ☐ Not started |
| M4 Package & publish | ☐ Not started |

## Stretch (optional, only if time allows)
- [ ] Add an SPC chart at the offending station showing the out-of-control signal that predicts the final defect.
- [ ] Scale-check the method on the anonymized Bosch Production Line Performance set.
