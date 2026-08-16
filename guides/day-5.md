# Day 5 — Isolation, cross-check & root-cause confirmation

**Goal:** confirm the driver with an independent model, pass the physics sanity
check, and write a precise root-cause statement plus the escape point. This is the
**D4 evidence** — the heart of the whole project.

**Time budget:** ~3–4 h (≈1.5 h cross-check, ≈1.5 h confirmation + figure).

**Covers:** `execution.md` §7–8 · **Milestone:** M2 finish.

**Where you left off:** a logistic model with odds ratios + CIs on the shortlist.

---

## 1. Tree cross-check → implement `stats.tree_crosscheck`

Fit an independent model and rank feature importances:

```python
from sklearn.ensemble import RandomForestClassifier   # or GradientBoostingClassifier
```

- Use `class_weight="balanced"` for the forest (imbalance again).
- Rank importances; a **permutation-importance** view (`sklearn.inspection.
  permutation_importance`) is more trustworthy than raw impurity importance —
  add it if time allows.

## 2. Require model agreement

Compare the logistic top driver to the tree's top driver. **They must agree** on the
prime suspect before you conclude (`execution.md` §7). If they disagree:
- re-check VIF / confounding (a collinear bystander may be stealing credit),
- check for a station you forgot to control for,
- only then reconsider the shortlist.

Agreement across two different model families is what makes the finding robust
rather than a model-specific artifact — and it's a great interview answer to *"how
did you avoid blaming the wrong step?"*

## 3. State the root cause precisely

Write it as: **Operation X, parameter Y, in condition Z** (e.g. *feed rate above
threshold*), with **odds ratio, 95% CI, and p** from the logistic model. Put a draft
straight into `reports/8D_Report.md` **D4** (with the numbers pulled from notebook
cells, not typed from memory).

## 4. Physics sanity check  ⚠️ hard gate

Does the sign/direction match machining reality? (e.g. higher feed → rougher
surface / oversize bore.) This is a **gate, not a formality** (`execution.md` §13):
if the effect contradicts physics, treat it as suspected confounding and go back to
the VIF / multivariate step before finalizing. A statistically "significant" result
that violates physics is a red flag, not a finding.

## 5. Escape point & the prize

- **Escape point:** why wasn't it caught earlier? The offending step lacked an
  in-line control/gate — name it. This becomes tomorrow's corrective-action target.
- **Quantify the prize:** estimate the defect-rate reduction from holding parameter
  Y in control (e.g. *"holding Y within ±σ removes the condition present in N% of
  failures"*).

## 6. The "smoking-gun" figure

Make one chart that *shows* the isolation — e.g. the fail-rate rising across bins of
parameter Y, or pass/fail distributions of Y side by side. Save it under
`reports/figures/`. This is the figure that sells the root cause at a glance.

---

## Tools today
- **scikit-learn** — `RandomForestClassifier` / `GradientBoostingClassifier`,
  `permutation_importance`.
- **statsmodels** — the odds ratios/CIs you carry from Day 4.
- **matplotlib / seaborn** — the smoking-gun figure.

## Hints & pitfalls
- **Two models, one story.** Don't skip the cross-check to save time — model
  agreement is the project's core credibility claim.
- **Permutation > impurity importance** for correlated features; impurity importance
  can be biased toward high-cardinality columns.
- **The physics gate is real.** A driver that "wins" statistically but makes no
  machining sense usually means confounding — fix it, don't rationalize it.
- Pull every number into D4 from a cell. If you can't point at the cell, it doesn't
  go in the report.

## Done checklist
- [ ] Tree model fit; importances (ideally permutation) ranked.
- [ ] Logistic and tree **agree** on the top driver.
- [ ] Root cause stated: station + parameter + condition, with OR/CI/p.
- [ ] Physics sanity check passed (or confounding resolved).
- [ ] Escape point named; prize quantified.
- [ ] Smoking-gun figure saved.

## What's next
→ [day-6.md](day-6.md): design the SPC corrective action and draft the full 8D
(D0–D8).
