# Day 4 — Finish the screen, start the logistic model

**Goal:** turn the raw per-parameter tests into a **corrected, effect-sized
shortlist**, then fit the first multivariate logistic model with a VIF check.

**Time budget:** ~3–4 h (≈1.5 h finish screen, ≈2 h logistic + VIF).

**Covers:** `execution.md` §6–7 · **Milestone:** M2 middle.

**Where you left off:** `stats.univariate_screen` returns raw p + effect sizes.

---

## 1. Multiple-comparison correction

You ran many tests, so some "significant" p-values are false positives. Add
correction inside `stats.univariate_screen`:

```python
from statsmodels.stats.multitest import multipletests
reject_fdr, p_fdr, *_ = multipletests(pvals, method="fdr_bh")   # primary
reject_bon, p_bon, *_ = multipletests(pvals, method="bonferroni")  # stricter cross-check
```

Return both adjusted p-columns.

## 2. Build the shortlist

Keep a parameter only if it **passes the corrected threshold AND has a non-trivial
effect** (Cohen's d ≥ ~0.2, or a meaningful Cramér's V). Sort by effect size and
save `reports/figures/univariate_ranking.png` (a ranked bar chart of effect size).

```python
ranking = stats.univariate_screen(parts)
shortlist = ranking.query("p_fdr < 0.05 and effect_size >= 0.2")["parameter"].tolist()
shortlist
```

## 3. Multicollinearity check → implement `stats.compute_vif`

Correlated station parameters "split the credit" and hide the true driver. Before
modeling, z-score the shortlisted continuous predictors and compute VIF:

```python
from statsmodels.stats.outliers_influence import variance_inflation_factor
```

**VIF > ~5** → drop or combine that predictor. Iterate until the surviving set is
clean. Record which you dropped and why (you'll mention this in D4 as part of "how I
avoided blaming a bystander").

## 4. First logistic model → implement `stats.fit_logistic`

Fit `fail ~ shortlisted parameters (+ station controls)` with `statsmodels`:

- **Standardize** continuous predictors (z-score) so coefficients compare directly.
- **Class imbalance:** failures are rare → fit with class weights; if very rare,
  also fit a penalized (L2) model to stabilize estimates.
- Read out **odds ratios = exp(coef)** with **95% CIs** and p-values.

```python
res = stats.fit_logistic(parts, shortlist)
res.summary()          # then exp the params + conf_int() for odds ratios
```

Don't conclude yet — the tree cross-check (Day 5) has to agree first.

---

## Tools today
- **statsmodels** — `multipletests`, `variance_inflation_factor`, `Logit`/`GLM`.
- **numpy / pandas** — z-scoring, assembling the design matrix.
- **matplotlib** — the ranking figure.

## Hints & pitfalls
- **FDR is primary, Bonferroni is the sanity check.** Report both; lead with FDR.
- **Standardize before you compare coefficients** — otherwise a big-unit parameter
  looks "important" just because of its scale.
- **Odds ratios need CIs.** A point OR with no interval is not evidence
  (`execution.md` §11). Report `exp(coef)` and `exp(conf_int())`.
- **Watch separation.** If a predictor perfectly splits pass/fail, statsmodels will
  warn and coefficients blow up — that's a sign to penalize or drop it.
- Keep the shortlist small (a handful). This is isolation, not a kitchen sink.

## Done checklist
- [ ] `univariate_screen` returns FDR + Bonferroni adjusted p-values.
- [ ] Shortlist built (corrected p **and** effect size); ranking figure saved.
- [ ] VIF computed; collinear predictors dropped/combined and noted.
- [ ] Logistic model fits; odds ratios + 95% CIs + p-values printed.

## What's next
→ [day-5.md](day-5.md): cross-check with a tree model, require agreement, and state
the confirmed root cause + escape point.
