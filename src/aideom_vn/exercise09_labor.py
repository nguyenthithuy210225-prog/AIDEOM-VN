"""Exercise 9: AI impact simulation for Vietnam labor markets."""

from __future__ import annotations

import numpy as np
import pandas as pd


def simulate_labor_impact(
    sectors: pd.DataFrame,
    adoption_rate: float = 0.45,
    training_budget: float = 30_000.0,
    ai_investment: float = 40_000.0,
) -> pd.DataFrame:
    """Compute job loss, job creation, and net jobs by sector."""
    df = sectors.copy()
    labor = df["labor_million"]
    risk = df["automation_risk_pct"] / 100
    readiness = df["ai_readiness_0_100"] / 100
    training_weight = labor * risk
    training_share = training_weight / training_weight.sum()
    ai_share = (df["ai_readiness_0_100"] + df["digital_index_0_100"]) / (
        df["ai_readiness_0_100"] + df["digital_index_0_100"]
    ).sum()
    df["job_loss_million"] = labor * risk * adoption_rate * 0.42
    df["training_alloc"] = training_budget * training_share
    df["ai_alloc"] = ai_investment * ai_share
    df["jobs_saved_million"] = df["training_alloc"] / 55_000 * (0.65 + readiness)
    df["new_jobs_million"] = df["ai_alloc"] / 80_000 * (0.35 + 0.9 * readiness)
    df["net_job_million"] = df["new_jobs_million"] + df["jobs_saved_million"] - df["job_loss_million"]
    return df.sort_values("net_job_million").reset_index(drop=True)


def find_training_threshold(
    sectors: pd.DataFrame,
    adoption_rate: float = 0.45,
    ai_investment: float = 40_000.0,
) -> dict:
    """Find minimum training budget so all sectors have non-negative NetJob."""
    for budget in np.arange(0, 250_001, 2_500):
        result = simulate_labor_impact(sectors, adoption_rate, budget, ai_investment)
        if result["net_job_million"].min() >= 0:
            return {"threshold": float(budget), "result": result}
    return {"threshold": np.nan, "result": simulate_labor_impact(sectors, adoption_rate, 250_000, ai_investment)}
