"""Stage 3 — statistical traceback helpers.

Covers execution.md §6 (Step 4, univariate screen) and §7 (Step 5, multivariate
isolation + tree cross-check). You implement these on Days 3–5.

These functions produce the D4 evidence for the 8D. Guiding rule: lead with
effect size, not just p-values, and never conclude on a single model.
"""

from __future__ import annotations

import pandas as pd


import numpy as np
import pandas as pd
from scipy import stats as sp_stats
from statsmodels.stats.multitest import multipletests


def univariate_screen(
    df: pd.DataFrame,
    target: str = "fail",
    features: list[str] | None = None,
    alpha: float = 0.05,
) -> pd.DataFrame:
    """Test every upstream parameter for a pass-vs-fail difference.

    For each parameter, picks the test by type (execution.md §6):
        continuous   -> Welch's t-test (unequal variance) & one-way ANOVA
                        reports: mean diff, t-stat, p-value, Cohen's d
        categorical  -> Chi-square test of independence
                        reports: chi2-stat, p-value, Cramer's V

    Controls the false-discovery rate across tests with Benjamini-Hochberg (FDR)
    and reports Bonferroni as the stricter cross-check.

    Parameters
    ----------
    df : pd.DataFrame
        Tidy parts table (e.g. from parts.parquet).
    target : str, default "fail"
        Binary label column name (1 = defect/rework, 0 = pass).
    features : list[str] | None, default None
        Specific features to test. If None, auto-selects process/measurement columns.
    alpha : float, default 0.05
        Family-wise significance threshold.

    Returns
    -------
    pd.DataFrame
        Ranked table: one row per parameter with statistics, raw p-value,
        FDR-adjusted p-value, Bonferroni-adjusted p-value, effect size, and significance.
    """
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found in DataFrame.")

    # Auto-select features if not specified
    if features is None:
        exclude_cols = {
            target,
            "part_id",
            "part_id_cylinder_bottom",
            "part_id_piston_rod",
            "cylinder_id",
            "assembly_rework",
            "rework",
        }
        # Exclude internal boolean qcpass flags from upstream process screening
        features = [
            c for c in df.columns
            if c not in exclude_cols and not c.endswith("_qcpass")
        ]

    results = []

    for col in features:
        if col not in df.columns:
            continue

        series = df[col]
        # Identify whether feature is categorical or continuous
        is_categorical = (
            series.dtype == "object"
            or series.dtype.name == "category"
            or "anomaly" in col
            or col.endswith("_missing")
            or series.nunique() <= 5
        )

        if is_categorical:
            # --- Categorical / Anomaly feature: Chi-Square Test & Cramer's V ---
            ct = pd.crosstab(df[col].fillna("Missing"), df[target])
            if ct.shape[0] < 2 or ct.shape[1] < 2:
                continue

            chi2, p_val, dof, _ = sp_stats.chi2_contingency(ct)
            n = ct.to_numpy().sum()
            min_dim = min(ct.shape[0] - 1, ct.shape[1] - 1)
            cramers_v = np.sqrt(chi2 / (n * min_dim)) if (n > 0 and min_dim > 0) else 0.0

            results.append({
                "parameter": col,
                "type": "categorical",
                "test": "Chi-Square",
                "statistic": float(chi2),
                "mean_diff": np.nan,
                "raw_p": float(p_val),
                "effect_size_type": "Cramer's V",
                "effect_size": float(cramers_v),
                "abs_effect_size": float(abs(cramers_v)),
            })
        else:
            # --- Continuous feature: Welch's t-test, ANOVA & Cohen's d ---
            pass_vals = df.loc[df[target] == 0, col].dropna()
            fail_vals = df.loc[df[target] == 1, col].dropna()

            if len(pass_vals) < 2 or len(fail_vals) < 2:
                continue

            # Welch's t-test (equal_var=False)
            t_stat, p_val = sp_stats.ttest_ind(pass_vals, fail_vals, equal_var=False)

            # Mean difference (fail - pass)
            mean_pass = pass_vals.mean()
            mean_fail = fail_vals.mean()
            mean_diff = mean_fail - mean_pass

            # Cohen's d (pooled standard deviation)
            n1, n2 = len(pass_vals), len(fail_vals)
            s1, s2 = pass_vals.std(ddof=1), fail_vals.std(ddof=1)
            pooled_var = ((n1 - 1) * (s1 ** 2) + (n2 - 1) * (s2 ** 2)) / (n1 + n2 - 2)
            pooled_sd = np.sqrt(pooled_var) if pooled_var > 0 else 1e-9
            cohen_d = mean_diff / pooled_sd

            results.append({
                "parameter": col,
                "type": "continuous",
                "test": "Welch t-test",
                "statistic": float(t_stat),
                "mean_diff": float(mean_diff),
                "raw_p": float(p_val),
                "effect_size_type": "Cohen's d",
                "effect_size": float(cohen_d),
                "abs_effect_size": float(abs(cohen_d)),
            })

    if not results:
        return pd.DataFrame()

    res_df = pd.DataFrame(results)

    # --- Multiple Comparison Corrections ---
    raw_p_values = res_df["raw_p"].values
    reject_fdr, p_fdr, _, _ = multipletests(raw_p_values, alpha=alpha, method="fdr_bh")
    reject_bonf, p_bonf, _, _ = multipletests(raw_p_values, alpha=alpha, method="bonferroni")

    res_df["p_fdr_bh"] = p_fdr
    res_df["p_bonferroni"] = p_bonf
    res_df["significant_fdr"] = reject_fdr
    res_df["significant_bonf"] = reject_bonf

    # Sort descending by absolute effect size
    res_df = res_df.sort_values("abs_effect_size", ascending=False).reset_index(drop=True)

    return res_df


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
