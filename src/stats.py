"""Stage 3 — statistical traceback helpers.

Univariate screening, multivariate isolation, and tree cross-check. These
functions produce the D4 evidence for the 8D. Guiding rule: lead with effect
size, not just p-values, and never conclude on a single model.
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

    For each parameter, picks the test by type:
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


import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor


def compute_vif(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Variance Inflation Factor for continuous predictors.

    Z-scores the predictors and computes VIF to assess multicollinearity.
    VIF > ~5 indicates collinear predictors that may confound multivariate attribution.

    Parameters
    ----------
    df : pd.DataFrame
        Tidy parts dataset.
    cols : list[str]
        Predictor column names to evaluate.

    Returns
    -------
    pd.DataFrame
        Table with 'parameter', 'VIF', and 'collinear_flag' (VIF >= 5.0).
    """
    valid_cols = [c for c in cols if c in df.columns]
    if not valid_cols:
        raise ValueError("No valid columns provided for VIF calculation.")

    # Extract and standardize predictors (z-score)
    X = df[valid_cols].copy()
    X_std = (X - X.mean()) / X.std(ddof=0).replace(0, 1e-9)
    X_const = sm.add_constant(X_std)

    vif_records = []
    for i, col_name in enumerate(X_const.columns):
        if col_name == "const":
            continue
        vif_val = float(variance_inflation_factor(X_const.values, i))
        vif_records.append({
            "parameter": col_name,
            "VIF": vif_val,
            "collinear_flag": vif_val >= 5.0,
        })

    vif_df = pd.DataFrame(vif_records).sort_values("VIF", ascending=False).reset_index(drop=True)
    return vif_df


def fit_logistic(
    df: pd.DataFrame,
    predictors: list[str],
    target: str = "fail",
) -> tuple[sm.discrete.discrete_model.BinaryResultsWrapper, pd.DataFrame]:
    """Fit multivariate logistic regression: fail ~ standardized predictors.

    Parameters
    ----------
    df : pd.DataFrame
        Tidy parts dataset.
    predictors : list[str]
        List of continuous or numeric process features to include in the model.
    target : str, default "fail"
        Binary outcome column name.

    Returns
    -------
    tuple[BinaryResultsWrapper, pd.DataFrame]
        The fitted statsmodels Logit result object and a summary DataFrame containing
        coefficients, standard errors, p-values, Odds Ratios (OR), and 95% CIs.
    """
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found in DataFrame.")

    valid_preds = [p for p in predictors if p in df.columns]
    if not valid_preds:
        raise ValueError("No valid predictor columns provided.")

    y = df[target].values
    X = df[valid_preds].copy()

    # Standardize predictors (z-score) so coefficients are directly comparable
    X_std = (X - X.mean()) / X.std(ddof=0).replace(0, 1e-9)
    X_const = sm.add_constant(X_std)

    # Fit Logistic Regression model
    model = sm.Logit(y, X_const).fit(disp=False)

    # Extract parameters, p-values, and 95% Confidence Intervals
    params = model.params
    pvalues = model.pvalues
    conf_int = model.conf_int()

    # Calculate Odds Ratios and 95% CI on odds ratio scale
    odds_ratios = np.exp(params)
    ci_lower = np.exp(conf_int[0])
    ci_upper = np.exp(conf_int[1])

    summary_df = pd.DataFrame({
        "parameter": params.index,
        "coef": params.values,
        "std_err": model.bse.values,
        "z_stat": model.tvalues.values,
        "p_value": pvalues.values,
        "Odds_Ratio": odds_ratios.values,
        "CI_lower_95": ci_lower.values,
        "CI_upper_95": ci_upper.values,
    })

    # Sort descending by significance (excluding intercept)
    summary_df = summary_df.sort_values("p_value", ascending=True).reset_index(drop=True)

    return model, summary_df


from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance


def tree_crosscheck(
    df: pd.DataFrame,
    predictors: list[str],
    target: str = "fail",
    n_estimators: int = 100,
    random_state: int = 42,
) -> pd.DataFrame:
    """Fit a Random Forest model and rank feature importances (Gini & Permutation).

    Provides an independent non-linear model family cross-check against the
    logistic regression model. Requires agreement on the primary suspect.

    Parameters
    ----------
    df : pd.DataFrame
        Tidy parts dataset.
    predictors : list[str]
        Predictor columns to evaluate.
    target : str, default "fail"
        Binary outcome column name.
    n_estimators : int, default 100
        Number of trees in the forest.
    random_state : int, default 42
        Seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        Ranked table: 'parameter', 'gini_importance', 'perm_importance_mean', 'perm_importance_std'.
    """
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found in DataFrame.")

    valid_preds = [p for p in predictors if p in df.columns]
    if not valid_preds:
        raise ValueError("No valid predictor columns provided.")

    X = df[valid_preds].copy()
    y = df[target].values

    # Fit Random Forest with balanced class weighting for rare events
    rf = RandomForestClassifier(
        n_estimators=n_estimators,
        class_weight="balanced",
        random_state=random_state,
    )
    rf.fit(X, y)

    # Compute ROC-AUC based permutation feature importance
    perm = permutation_importance(
        rf,
        X,
        y,
        scoring="roc_auc",
        n_repeats=20,
        random_state=random_state,
    )

    importance_df = pd.DataFrame({
        "parameter": valid_preds,
        "gini_importance": rf.feature_importances_,
        "perm_importance_mean": perm.importances_mean,
        "perm_importance_std": perm.importances_std,
    })

    # Sort descending by permutation importance
    importance_df = importance_df.sort_values(
        "perm_importance_mean", ascending=False
    ).reset_index(drop=True)

    return importance_df

