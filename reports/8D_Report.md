# 8D Corrective Action Report — Sentinel-8D

> **AIAG-format Eight Disciplines (8D) report.** Every number in D2 and D4 traces
> to a cell in `notebooks/01_traceback.ipynb` (execution.md §11). Fill each
> discipline as you reach it; the "source" note points at the analysis step that
> produces the content. Render to `reports/8D_Report.pdf` on Day 7.

| Field | Value |
|-------|-------|
| Report ID | 8D-2026-CIP-001 |
| Product / part | Pneumatic Cylinder Assembly (Cylinder Bottom + Piston Rod) |
| Dataset | CiP-DMD (TU Darmstadt, DOI: 10.5281/zenodo.8420132) |
| Author | Siddardth Pathipaka |
| Date opened | 2026-08-16 |
| Status | In Progress (D0–D2 Complete) |

---

## D0 — Symptom & emergency response action
*Source: notebook Step 3 (defect characterization).*

- **Symptom**: During end-of-line functional acceptance and final pneumatic testing, a significant proportion of assembled cylinders exhibited assembly non-conformities requiring manual disassembly and component rework.
- **Emergency Response Action (ERA)**: Immediate containment trigger: flagged all finished units from active production lots for 100% functional verification prior to packaging and release; quarantined suspect assembled cylinders requiring rework.

## D1 — Team
*Cross-functional problem solving team roles established:*

- **Executive Champion**: Plant Quality Director (resource allocation, barrier removal, final 8D sign-off).
- **Lead Quality Engineer**: Siddardth Pathipaka (8D ownership, statistical traceback, measurement system analysis).
- **Process / Machining Engineer**: CNC Specialist (tooling, cutting feeds/speeds, milling jig clamping inspection).
- **Assembly Operations Lead**: Line Supervisor (assembly protocol adherence, pneumatic pressure testing oversight).
- **Data Analyst**: Quality Data Lead (statistical screening, multi-station join modeling, SPC implementation).

## D2 — Problem description (5W2H)
*Source: notebook Step 3 — baseline rate, failure count, total parts.*

| 5W2H | Description / Evidence |
|:---|:---|
| **What** (Failure Mode) | Pneumatic cylinder functional defect requiring assembly rework (`assembly_rework == 'y'`). |
| **Where** (Location) | Final Cylinder Assembly & Testing Station (downstream of Sawing, CNC Milling, and CNC Lathe operations). |
| **When** (Timing) | Observed across production batch of 802 assembled units (CiP-DMD trial run). |
| **Who** (Ownership) | Assembly Operations & Manufacturing Quality Engineering. |
| **Why** (Severity / Impact) | High rework cost, line stoppage risk, assembly cycle disruption, and risk of escaping dimensional defects. |
| **How** (Detection Method) | Post-assembly inspection & pneumatic pressure testing protocol (`assembly_qc.csv`). |
| **How many** (Volume / Rate) | **52 defective units out of 802 total assembled parts** = **6.48% baseline defect rate** (64,838 DPMO). |

## D3 — Interim containment action
*Framed containment protocol:*

1. **100% In-Line Inspection**: Implemented mandatory weight scale check at Saw Station output (quarantine parts with weight $< 0.520$ kg) and dimensional verification at CNC Lathe output.
2. **Quarantine & Sorting**: Quarantined current buffer inventory of cylinder bottoms and piston rods produced under suspect machine runs.
3. **Traceability Tagging**: Mandated 2D DataMatrix scanning at every machine handover to ensure 100% component-to-assembly traceability.

## D4 — Root cause & escape point (Preliminary Isolation)
*Source: notebook Steps 4–5 (Univariate Screening + Multivariate Logistic Isolation).*

- **Multicollinearity Diagnostic**: Variance Inflation Factor (VIF) evaluated for all candidate predictors; all $\text{VIF} \in [1.02, 1.09] \ll 5.0$, confirming no multicollinearity distortion.
- **Multivariate Logistic Model ($N=802$, Pseudo $R^2 = 0.185, p = 2.51 \times 10^{-13}$)**:
  - **Primary Suspect 1 — Saw Weight (`saw_weight`)**: $\text{OR} = \mathbf{0.503}$ (95% CI: $[0.371, 0.683]$, $p = 1.00 \times 10^{-5}$). Each $1\sigma$ decrease in cut blank weight nearly doubles the odds of assembly rework ($\text{OR}_{\text{decrease}} = 1.99$).
  - **Primary Suspect 2 — Lathe Length (`lathe_length`)**: $\text{OR} = \mathbf{0.562}$ (95% CI: $[0.419, 0.753]$, $p = 1.17 \times 10^{-4}$).
  - **Primary Suspect 3 — Lathe Diameter (`lathe_diameter`)**: $\text{OR} = \mathbf{1.502}$ (95% CI: $[1.079, 2.091]$, $p = 0.0158$).
  - **Milling Surface Roughness (`mill_surface_roughness`)**: $\text{OR} = 0.436$ (95% CI: $[0.204, 0.933]$, $p = 0.0324$).
- **Escape Point**: Sawing station lacked an automatic weight gate or part length stop sensor, allowing short blanks to escape into CNC Milling and downstream Assembly.

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
