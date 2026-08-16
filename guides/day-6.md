# Day 6 — Corrective action & authoring the 8D

**Goal:** design the permanent corrective action (an SPC control at the offending
step) and write the full 8D report, D0–D8, with every number traced to the notebook.

**Time budget:** ~3–4 h (≈1 h SPC design, ≈2.5 h authoring).

**Covers:** `execution.md` §9–10 · **Milestone:** M3.

**Where you left off:** a confirmed root cause + escape point + smoking-gun figure.

---

## 1. Design the SPC control (D5) → notebook Step 7

Specify a concrete, shop-floor control at the offending operation:
- **Chart type:** e.g. **I-MR** (individuals) or **X̄-R** (subgrouped) on parameter Y.
  Pick based on whether parts are measured individually or in subgroups.
- **Control limits:** compute them from the **in-control subset** of the data (the
  passing parts / stable period) — not from all data, or the out-of-control points
  will inflate the limits.
- **Reaction plan:** what the operator does when a point goes out of limits.

Put the limits and chart spec in the notebook so they're reproducible, and (bonus,
`roadmap.md` stretch) plot the chart showing the out-of-control signal that precedes
the final defect.

## 2. Validation logic (D6)

Show the expected effect: the failures concentrate in the out-of-control region, so
holding parameter Y in control removes them. Reuse the "prize" estimate from Day 5.
This is a *logical* validation on historical data — you're not deploying anything.

## 3. Prevent recurrence (D7)

State the systemic fix: update the **Control Plan** and **PFMEA** at that station.
This is the explicit hand-off to **Project 2** — call it out by name.

## 4. Author the full 8D → `reports/8D_Report.md`

Fill every discipline. The template already has the headings and a source note per
discipline. Map (from `execution.md` §10):

| Discipline | Content | Source |
|-----------|---------|--------|
| D0 | Symptom / emergency response | Step 3 |
| D1 | Cross-functional team & roles (framed) | — |
| D2 | Problem description (5W2H + baseline rate/volume) | Step 3 |
| D3 | Interim containment (100% inspection / quarantine) | — |
| D4 | Root cause + escape point (the statistics) | Steps 4–6 |
| D5 | Permanent corrective action (SPC control) | Step 7 |
| D6 | Validate the corrective action | Steps 6–7 |
| D7 | Prevent recurrence (Control Plan / PFMEA) | Step 7 → Project 2 |
| D8 | Closure & recognition; archive evidence | — |

**Write for four readers at once** (`idea.md` §3): quality engineer, supplier
quality engineer, process engineer, and a QMS auditor. It must read cleanly to a
non-analyst — explain the statistics in plain language, keep the exact figures.

---

## Tools today
- **numpy / pandas** — control-limit math from the in-control subset.
- **matplotlib** — the optional SPC chart.
- **Markdown** — authoring `8D_Report.md`.

## Hints & pitfalls
- **Limits from the in-control subset only.** Computing control limits from data
  that includes the failures defeats the purpose — the special-cause points widen
  the limits and hide the signal.
- **D4 is the payload; D7 is the point.** A statistically proven D4 is what makes
  D7 credible to a customer (`idea.md` §4). Don't shortchange recurrence prevention.
- **No hand-typed numbers.** Copy figures from notebook outputs; if a number isn't
  in a cell, generate it or cut it.
- **Plain language wins.** An auditor rejects "we think it was operator error";
  they accept "Operation 30 feed rate, OR 3.4 (95% CI 1.9–6.1), p < 0.001, with an
  SPC control at the escape point."

## Done checklist
- [ ] SPC chart type + control limits (from in-control subset) + reaction plan
      specified in the notebook.
- [ ] D5, D6, D7 written with the SPC control and the PFMEA/Control-Plan hand-off.
- [ ] All of D0–D8 filled in `reports/8D_Report.md`.
- [ ] Every statistic in the report traces to a notebook cell.

## What's next
→ [day-7.md](day-7.md): render the PDF, clean the notebook, write the README result
+ résumé bullet, and tag `v1.0`.
