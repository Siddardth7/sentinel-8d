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

## D4 — Root cause & escape point (Confirmed Statistical Evidence)
*Source: notebook Steps 4–6 (Univariate Screening → Multivariate Isolation → Tree Cross-Check → Root Cause Confirmation).*

### 1. Primary Root Cause Statement
- **Offending Operation**: **Sawing Station (Kasto SBA 2)**
- **Offending Parameter**: **Saw Cut Blank Weight (`saw_weight`)**
- **Root-Cause Condition**: Undersized saw blanks ($< 0.540$ kg, vs. nominal $0.580$ kg) resulting from bar stock feed misalignment.
- **Statistical Evidence**:
  - **Odds Ratio**: $\mathbf{0.503}$ ($95\%\text{ CI: } [\mathbf{0.371}, \mathbf{0.683}], \mathbf{p = 1.00 \times 10^{-5}}$).
  - Each $1\sigma$ decrease ($0.024$ kg) in blank weight increases the odds of final assembly failure by **$1.99\times$** ($+98.7\%$).

### 2. Multi-Model Agreement (Independent Machine Learning Validation)
All three independent model families unanimously rank **`saw_weight`** as the **#1 primary driver**:

| Model Family | Role / Evaluation Metric | Rank #1 Feature | Top Feature Metric | Significance / Stability |
|:---|:---|:---:|:---|:---:|
| **Multivariate Logistic Regression** | Generalized Linear Model ($\text{OR} = e^\beta$) | **`saw_weight`** | $\text{OR} = 0.503$ (95% CI: $0.371–0.683$) | $p = 1.00 \times 10^{-5}$ |
| **Random Forest (Balanced)** | ROC-AUC Permutation Importance | **`saw_weight`** | Permutation $\Delta\text{AUC} = 0.0707 \pm 0.011$ | Gini Impurity $= 0.242$ |
| **Gradient Tree Boosting** | Ensembled Gradient Boosted Trees | **`saw_weight`** | Permutation $\Delta\text{AUC} = 0.0579 \pm 0.010$ | Gini Impurity $= 0.304$ |

### 3. Engineering Physics Sanity Check
- **Physical Mechanism**: The cylinder bottom raw blank is cut from bar stock at the saw. When bar stock is misaligned against the backstop, blanks are cut too short (`saw_weight` $< 0.540$ kg). In the subsequent CNC milling step (DMC 50H), the undersized blank fails to achieve standard clamping depth in the hydraulic fixture. This causes fixture slippage, chatter, face non-parallelism, and seal groove distortion. When assembled with the piston rod, the distorted bottom face causes pneumatic stroke binding and seal leakage, forcing mandatory disassembly and rework.
- **Verdict**: **PASSED**. The negative sign ($\beta = -0.687, \text{OR} < 1.0$) perfectly reflects physical machining and clamping mechanics.

### 4. Escape Point & Prize Quantification
- **Escape Point**: The Sawing Station (Kasto SBA 2) lacked an in-line weight check scale or laser length stop interlock. Undersized blanks escaped undetected into CNC Milling and downstream Assembly.
- **Quantification of the Prize**:
  - Parts with `saw_weight` $< 0.540$ kg exhibit an assembly failure rate of **$15.6\%$** (compared to $4.9\%$ for $\ge 0.540$ kg and $2.4\%$ for nominal parts).
  - Implementing 100% in-line weight control at the saw eliminates **$36.5\%$ of all assembly rework defects** ($19$ out of $52$ failures eliminated immediately).

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
