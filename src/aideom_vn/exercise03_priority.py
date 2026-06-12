"""Exercise 3: sector priority index."""

from __future__ import annotations

import pandas as pd

DEFAULT_COLUMNS = [
    "growth_rate_2024_pct",
    "labor_share_pct",
    "spillover_coef_0_1",
    "export_billion_USD",
    "ai_readiness_0_100",
    "automation_risk_pct",
]

DEFAULT_WEIGHTS = [0.18, 0.12, 0.18, 0.18, 0.22, 0.12]
DEFAULT_COST_COLUMNS = {"automation_risk_pct"}


def minmax(series: pd.Series) -> pd.Series:
    """Min-max normalize a numeric series to [0, 1]."""
    denom = series.max() - series.min()
    if denom == 0:
        return pd.Series(0.0, index=series.index)
    return (series - series.min()) / denom


def inverse_minmax(series: pd.Series) -> pd.Series:
    """Min-max normalize a cost/risk criterion where lower is better."""
    denom = series.max() - series.min()
    if denom == 0:
        return pd.Series(0.0, index=series.index)
    return (series.max() - series) / denom


def compute_priority(
    df: pd.DataFrame,
    columns: list[str],
    weights: list[float],
    cost_columns: set[str] | None = None,
) -> pd.DataFrame:
    """Compute a weighted priority score after min-max normalization."""
    cost_columns = cost_columns or set()
    if len(columns) != len(weights):
        raise ValueError("columns and weights must have the same length")

    normalized = pd.DataFrame(index=df.index)
    for column in columns:
        if column in cost_columns:
            normalized[column] = inverse_minmax(df[column])
        else:
            normalized[column] = minmax(df[column])

    score = sum(normalized[column] * weight for column, weight in zip(columns, weights))
    result = df.copy()
    result["priority_score"] = score
    result["rank"] = result["priority_score"].rank(ascending=False, method="dense")
    return result.sort_values("priority_score", ascending=False).reset_index(drop=True)


def normalized_priority_matrix(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    cost_columns: set[str] | None = None,
) -> pd.DataFrame:
    """Return the normalized criteria matrix used by the priority model."""
    columns = DEFAULT_COLUMNS if columns is None else columns
    cost_columns = DEFAULT_COST_COLUMNS if cost_columns is None else cost_columns
    normalized = pd.DataFrame({"sector_name_vi": df["sector_name_vi"]})
    for column in columns:
        if column in cost_columns:
            normalized[column] = inverse_minmax(df[column])
        else:
            normalized[column] = minmax(df[column])
    return normalized


def run_priority_model(
    sectors: pd.DataFrame,
    weights: list[float] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute priority ranking using default exercise criteria."""
    weights = DEFAULT_WEIGHTS if weights is None else weights
    total = sum(weights)
    weights = [weight / total for weight in weights] if total else DEFAULT_WEIGHTS
    ranked = compute_priority(sectors, DEFAULT_COLUMNS, weights, DEFAULT_COST_COLUMNS)
    normalized = normalized_priority_matrix(sectors, DEFAULT_COLUMNS, DEFAULT_COST_COLUMNS)
    return ranked, normalized


def sensitivity_top_sectors(sectors: pd.DataFrame) -> pd.DataFrame:
    """Run a compact policy-weight sensitivity analysis."""
    scenarios = {
        "Cơ sở": DEFAULT_WEIGHTS,
        "Ưu tiên tăng trưởng": [0.30, 0.10, 0.15, 0.20, 0.15, 0.10],
        "Ưu tiên AI": [0.12, 0.08, 0.15, 0.15, 0.38, 0.12],
        "Ưu tiên việc làm": [0.12, 0.30, 0.18, 0.12, 0.14, 0.14],
        "Giảm rủi ro": [0.12, 0.14, 0.16, 0.12, 0.14, 0.32],
    }
    rows = []
    for scenario, weights in scenarios.items():
        ranked, _ = run_priority_model(sectors, weights)
        top = ranked.iloc[0]
        rows.append(
            {
                "scenario": scenario,
                "top_sector": top["sector_name_vi"],
                "top_score": top["priority_score"],
                "top3": ", ".join(ranked.head(3)["sector_name_vi"].tolist()),
            }
        )
    return pd.DataFrame(rows)
