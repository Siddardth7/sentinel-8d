# 8D Corrective Action Report — Sentinel-8D

> **AIAG-format Eight Disciplines (8D) report.** Every number in D2 and D4 traces
> to a cell in `notebooks/01_traceback.ipynb` (execution.md §11). Fill each
> discipline as you reach it; the "source" note points at the analysis step that
> produces the content. Render to `reports/8D_Report.pdf` on Day 7.

| Field | Value |
|-------|-------|
| Report ID | _TODO_ |
| Product / part | _TODO (e.g. pneumatic cylinder)_ |
| Dataset | _TODO: name, version/date, URL_ |
| Author | Siddardth Pathipaka |
| Date opened | _TODO_ |
| Status | Draft |

---

## D0 — Symptom & emergency response action
*Source: notebook Step 3 (defect characterization).*

_TODO: the trigger — a fraction of finished parts fail final QC on a specific
characteristic. State the symptom and any immediate emergency response._

## D1 — Team
*Framed (no live team on a case study). Name the roles a real 8D would staff.*

_TODO: champion, quality engineer, process engineer, data analyst — and why
each is needed._

## D2 — Problem description (5W2H)
*Source: notebook Step 3 — baseline rate, failure count, total parts.*

| 5W2H | Answer |
|------|--------|
| What | _TODO: the failure mode_ |
| Where | _TODO: final QC, on characteristic X_ |
| When | _TODO: over what lot/period_ |
| Who | _TODO_ |
| Why (matters) | _TODO: cost / recurrence_ |
| How | _TODO: how detected_ |
| How many | _TODO: N failures / total, = baseline rate %_ |

## D3 — Interim containment action
*Framed.*

_TODO: 100% inspection / lot quarantine until root cause is closed._

## D4 — Root cause & escape point
*Source: notebook Steps 4–6 (univariate screen → multivariate isolation → confirmation). This is the statistical heart of the report.*

- **Root cause:** _TODO: Operation X, parameter Y, in condition Z_ — odds ratio
  **_TODO_** (95% CI _TODO_), **p _TODO_** (< 0.05 after FDR correction).
- **Model agreement:** logistic regression and the tree cross-check both rank
  _TODO_ as the top driver.
- **Physics sanity check:** _TODO — the sign/direction matches machining reality
  because ..._
- **Escape point:** _TODO — the offending step lacked an in-line control/gate, so
  the defect was not caught until final QC._

## D5 — Permanent corrective action
*Source: notebook Step 7.*

_TODO: SPC control at the offending operation — chart type (e.g. I-MR or X̄-R on
parameter Y), control limits from the in-control subset, and the reaction plan._

## D6 — Validate the corrective action
*Source: notebook Steps 6–7.*

_TODO: expected defect-rate reduction — failures concentrate in the
out-of-control region; holding parameter Y in control removes the condition
present in N% of failures._

## D7 — Prevent recurrence
*Hand-off to Project 2 (PFMEA + Control Plan).*

_TODO: update the Control Plan and PFMEA at that station to institutionalize the
new control._

## D8 — Closure & recognition
*Framed.*

_TODO: confirm the loop is closed; archive the notebook + figures as evidence;
recognize the team._
