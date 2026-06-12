"""Exercise 6: TOPSIS ranking for Vietnam regions."""

from __future__ import annotations

import numpy as np
import pandas as pd


TOPSIS_CRITERIA = [
    "grdp_growth_pct",
    "grdp_per_capita_million_VND",
    "fdi_registered_billion_USD",
    "exports_billion_USD",
    "digital_index_0_100",
    "ai_readiness_0_100",
    "trained_labor_pct",
    "rd_intensity_pct",
    "internet_penetration_pct",
    "gini_coef",
]

COST_CRITERIA = {"gini_coef"}


def entropy_weights(matrix: pd.DataFrame) -> pd.Series:
    """Compute objective entropy weights for a non-negative criteria matrix."""
    x = matrix.astype(float).to_numpy()
    x = x / np.maximum(x.sum(axis=0), 1e-12)
    entropy = -(x * np.log(np.maximum(x, 1e-12))).sum(axis=0) / np.log(len(matrix))
    diversity = 1 - entropy
    weights = diversity / diversity.sum()
    return pd.Series(weights, index=matrix.columns)


def run_topsis(
    regions: pd.DataFrame,
    weights: pd.Series | None = None,
) -> tuple[pd.DataFrame, pd.Series]:
    """Rank regions using TOPSIS with entropy weights by default."""
    raw = regions[TOPSIS_CRITERIA].astype(float).copy()
    adjusted = raw.copy()
    for col in COST_CRITERIA:
        adjusted[col] = adjusted[col].max() - adjusted[col] + adjusted[col].min()
    norm = adjusted / np.sqrt((adjusted**2).sum(axis=0))
    weights = entropy_weights(adjusted) if weights is None else weights.reindex(TOPSIS_CRITERIA)
    weighted = norm * weights
    ideal_best = weighted.max(axis=0)
    ideal_worst = weighted.min(axis=0)
    d_plus = np.sqrt(((weighted - ideal_best) ** 2).sum(axis=1))
    d_minus = np.sqrt(((weighted - ideal_worst) ** 2).sum(axis=1))
    score = d_minus / (d_plus + d_minus)
    ranking = regions[["region_id", "region_name_vi"]].copy()
    ranking["TOPSIS_score"] = score
    ranking["D_plus"] = d_plus
    ranking["D_minus"] = d_minus
    ranking["rank"] = ranking["TOPSIS_score"].rank(ascending=False, method="dense")
    ranking = ranking.sort_values("TOPSIS_score", ascending=False).reset_index(drop=True)
    return ranking, weights
