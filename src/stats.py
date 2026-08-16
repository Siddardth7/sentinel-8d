"""Stage 3 — statistical traceback helpers.

Covers execution.md §6 (Step 4, univariate screen) and §7 (Step 5, multivariate
isolation + tree cross-check). You implement these on Days 3–5.

These functions produce the D4 evidence for the 8D. Guiding rule: lead with
effect size, not just p-values, and never conclude on a single model.
"""

from __future__ import annotations

import pandas as pd


def univariate_screen(df: pd.DataFrame, target: str = "fail") -> pd.DataFrame:
    """Test every upstream parameter for a pass-vs-fail difference.

    For each parameter, pick the test by type (execution.md §6):
        continuous   -> Welch's t-test (unequal variance) / one-way ANOVA
                        report: mean diff, t/F, p, Cohen's d
        categorical  -> chi-square test of independence
                        report: chi2, p, Cramer's V

    Then control the false-discovery rate across the many tests with
    Benjamini-Hochberg (statsmodels.stats.multitest.multipletests, method="fdr_bh")
    and report Bonferroni as the stricter cross-check.

    Returns
    -------
    pandas.DataFrame
        One row per parameter: raw p, adjusted p (FDR + Bonferroni), effect size.
        Sort by effect size to build the shortlist.

    Shortlist rule: keep parameters that pass the corrected threshold AND show a
    non-trivial effect (d >= ~0.2 or a meaningful Cramer's V). A tiny p on a huge
    N is not enough.

    TODO(day-3/4): implement per-type dispatch + multiple-comparison correction.
    """
    raise NotImplementedError("Implement on Day 3/4 — see guides/day-3.md")


def compute_vif(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Variance Inflation Factor for the shortlisted continuous predictors.

    Use statsmodels.stats.outliers_influence.variance_inflation_factor.
    VIF > ~5 means predictors are collinear and would split the credit, hiding
    the true driver — drop or combine before fitting the logistic model.

    TODO(day-4): z-score predictors first; return VIF per column.
    """
    raise NotImplementedError("Implement on Day 4 — see guides/day-4.md")


def fit_logistic(df: pd.DataFrame, predictors: list[str], target: str = "fail"):
    """Logistic regression: fail ~ shortlisted parameters (+ station controls).

    Pre-model hygiene (execution.md §7):
      - standardize (z-score) continuous predictors so coefficients compare
      - handle class imbalance with class weights; if failures are very rare,
        also fit a penalized (L2) model to stabilize estimates
    Read-out: odds ratios with 95% CIs and p-values. The prime suspect is the
    parameter with the largest, most significant, CI-excluding-1 effect.

    Returns the fitted statsmodels result (so the notebook can pull OR/CI/p).

    TODO(day-4/5): fit via statsmodels Logit/GLM; return the result object.
    """
    raise NotImplementedError("Implement on Day 4/5 — see guides/day-4.md")


def tree_crosscheck(df: pd.DataFrame, predictors: list[str], target: str = "fail"):
    """Fit a gradient-boosted / random-forest model and rank feature importances.

    Purpose: an independent second opinion on the top driver. REQUIRE agreement
    between this and the logistic model before concluding (execution.md §7) —
    this guards against a model-specific artifact. A permutation-importance or
    SHAP view is a good robustness add-on.

    Returns importances aligned to `predictors`, sorted descending.

    TODO(day-5): fit sklearn model; return importance ranking.
    """
    raise NotImplementedError("Implement on Day 5 — see guides/day-5.md")
