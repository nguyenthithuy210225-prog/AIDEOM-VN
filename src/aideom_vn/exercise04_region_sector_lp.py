"""Exercise 4: LP allocation across regions, sectors, and investment items."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import linprog

from .exercise03_priority import run_priority_model


ITEM_EFFECTS = pd.DataFrame(
    {
        "item": ["I", "D", "AI", "H"],
        "item_name": ["Hạ tầng số", "Chuyển đổi số DN", "Năng lực AI", "Nhân lực số"],
        "effect": [0.90, 1.05, 1.28, 1.00],
        "min_share": [0.18, 0.20, 0.15, 0.15],
    }
)


def _build_variables(regions: pd.DataFrame, sectors: pd.DataFrame) -> pd.DataFrame:
    priority, _ = run_priority_model(sectors)
    sector_scores = priority.set_index("sector_id")["priority_score"].to_dict()
    viable_sectors = sectors[sectors["growth_rate_2024_pct"] > 0].copy()
    rows = []
    for _, region in regions.iterrows():
        equity_boost = 1 + (100 - region["digital_index_0_100"]) / 180
        readiness = 0.55 + region["ai_readiness_0_100"] / 200
        for _, sector in viable_sectors.iterrows():
            sector_score = sector_scores[sector["sector_id"]]
            for _, item in ITEM_EFFECTS.iterrows():
                coef = (
                    item["effect"]
                    * (0.45 + sector_score)
                    * readiness
                    * equity_boost
                    * (1 + sector["spillover_coef_0_1"] / 3)
                )
                rows.append(
                    {
                        "region_id": region["region_id"],
                        "region_name_vi": region["region_name_vi"],
                        "sector_id": sector["sector_id"],
                        "sector_name_vi": sector["sector_name_vi"],
                        "item": item["item"],
                        "item_name": item["item_name"],
                        "coef": coef,
                    }
                )
    return pd.DataFrame(rows)


def solve_region_sector_lp(
    regions: pd.DataFrame,
    sectors: pd.DataFrame,
    budget: float = 50_000.0,
    weak_region_floor: float = 0.09,
    max_region_share: float = 0.32,
    max_sector_share: float = 0.35,
    min_region_share: float = 0.04,
) -> dict:
    """Solve a medium-sized LP for sector-region digital investment allocation."""
    variables = _build_variables(regions, sectors)
    n = len(variables)
    c = -variables["coef"].to_numpy()
    a_ub: list[np.ndarray] = []
    b_ub: list[float] = []

    a_ub.append(np.ones(n))
    b_ub.append(budget)

    for region_id in regions["region_id"]:
        mask = (variables["region_id"] == region_id).to_numpy(dtype=float)
        a_ub.append(mask)
        b_ub.append(budget * max_region_share)
        a_ub.append(-mask)
        b_ub.append(-budget * min_region_share)

    for sector_id in variables["sector_id"].unique():
        mask = (variables["sector_id"] == sector_id).to_numpy(dtype=float)
        a_ub.append(mask)
        b_ub.append(budget * max_sector_share)

    weak_regions = regions.nsmallest(2, "digital_index_0_100")["region_id"].tolist()
    for region_id in weak_regions:
        mask = -(variables["region_id"] == region_id).to_numpy(dtype=float)
        a_ub.append(mask)
        b_ub.append(-budget * weak_region_floor)

    for _, item in ITEM_EFFECTS.iterrows():
        mask = -(variables["item"] == item["item"]).to_numpy(dtype=float)
        a_ub.append(mask)
        b_ub.append(-budget * item["min_share"])

    result = linprog(c, A_ub=np.vstack(a_ub), b_ub=np.array(b_ub), bounds=[(0, None)] * n, method="highs")
    if not result.success:
        return {"success": False, "message": result.message}

    allocation = variables.copy()
    allocation["allocation"] = result.x
    allocation = allocation[allocation["allocation"] > 1e-6].copy()
    allocation["gdp_gain"] = allocation["allocation"] * allocation["coef"]
    return {
        "success": True,
        "objective": float(-result.fun),
        "allocation": allocation.sort_values("allocation", ascending=False).reset_index(drop=True),
        "region_summary": allocation.groupby("region_name_vi", as_index=False)["allocation"].sum(),
        "sector_summary": allocation.groupby("sector_name_vi", as_index=False)["allocation"].sum(),
        "item_summary": allocation.groupby("item_name", as_index=False)["allocation"].sum(),
        "weak_regions": weak_regions,
    }
