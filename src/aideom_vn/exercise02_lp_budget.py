"""Exercise 2: simple LP budget allocation."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import linprog


def solve_simple_budget_lp(
    budget: float = 100.0,
    min_human: float = 20.0,
    solver: str = "pulp",
):
    """Solve the four-item digital investment LP.

    PuLP/CBC is used first because it exposes LP dual values in a form familiar
    for coursework. SciPy/HiGHS remains available as a fallback and comparison
    solver.
    """
    if solver == "pulp":
        try:
            return solve_simple_budget_lp_pulp(budget=budget, min_human=min_human)
        except Exception as exc:
            result = solve_simple_budget_lp_scipy(budget=budget, min_human=min_human)
            result["message"] = f"PuLP unavailable, used SciPy/HiGHS fallback. {result['message']} ({exc})"
            return result
    if solver == "scipy":
        return solve_simple_budget_lp_scipy(budget=budget, min_human=min_human)
    raise ValueError("solver must be 'pulp' or 'scipy'")


def solve_simple_budget_lp_scipy(budget: float = 100.0, min_human: float = 20.0):
    """Solve the four-item digital investment LP with SciPy/HiGHS."""
    c = [-0.85, -1.20, -0.95, -1.35]
    a_ub = [
        [1, 1, 1, 1],
        [-1, 0, 0, 0],
        [0, -1, 0, 0],
        [0, 0, -1, 0],
        [0, 0, 0, -1],
        [0.35, -0.65, 0.35, -0.65],
    ]
    b_ub = [budget, -25, -15, -min_human, -10, 0]
    result = linprog(c, A_ub=a_ub, b_ub=b_ub, bounds=[(0, None)] * 4, method="highs")
    if not result.success:
        return {"success": False, "message": result.message}
    shadow_prices = None
    if hasattr(result, "ineqlin"):
        # HiGHS solves the minimization of -Z, so signs are flipped back to max-Z.
        shadow_prices = np.round(-result.ineqlin.marginals, 6)
    return {
        "success": True,
        "allocation": np.round(result.x, 6),
        "objective": float(-result.fun),
        "slack": _standard_constraint_slack(result.x, budget, min_human),
        "shadow_prices": shadow_prices,
        "solver": "scipy.linprog_highs",
        "shadow_price_source": "HiGHS ineqlin marginal, sign-adjusted from min -Z",
        "message": result.message,
    }


def solve_simple_budget_lp_pulp(budget: float = 100.0, min_human: float = 20.0):
    """Solve the LP with PuLP/CBC and return primal, slack, and dual values."""
    import pulp

    items = ["x1", "x2", "x3", "x4"]
    coeff = {"x1": 0.85, "x2": 1.20, "x3": 0.95, "x4": 1.35}
    model = pulp.LpProblem("bai02_digital_budget_lp", pulp.LpMaximize)
    x = {item: pulp.LpVariable(item, lowBound=0) for item in items}
    model += pulp.lpSum(coeff[item] * x[item] for item in items), "GDP_gain"

    constraints = [
        ("budget_total", pulp.lpSum(x[item] for item in items) <= budget),
        ("min_infra", x["x1"] >= 25),
        ("min_ai_data", x["x2"] >= 15),
        ("min_human", x["x3"] >= min_human),
        ("min_rd", x["x4"] >= 10),
        ("ai_rd_share", x["x2"] + x["x4"] >= 0.35 * budget),
    ]
    for name, constraint in constraints:
        model += constraint, name

    status = model.solve(pulp.PULP_CBC_CMD(msg=False))
    if pulp.LpStatus[status] != "Optimal":
        return {"success": False, "message": pulp.LpStatus[status]}

    allocation = np.array([pulp.value(x[item]) for item in items], dtype=float)
    shadow_prices = np.array([model.constraints[name].pi for name, _ in constraints], dtype=float)
    return {
        "success": True,
        "allocation": np.round(allocation, 6),
        "objective": float(pulp.value(model.objective)),
        "slack": _standard_constraint_slack(allocation, budget, min_human),
        "shadow_prices": np.round(shadow_prices, 6),
        "solver": "PuLP_CBC",
        "shadow_price_source": "PuLP/CBC constraint pi",
        "message": "Optimal",
    }


def _standard_constraint_slack(
    allocation: np.ndarray,
    budget: float,
    min_human: float,
) -> np.ndarray:
    """Return non-negative slack/surplus in the displayed constraint order."""
    x1, x2, x3, x4 = np.asarray(allocation, dtype=float)
    slack = np.array(
        [
            budget - (x1 + x2 + x3 + x4),
            x1 - 25,
            x2 - 15,
            x3 - min_human,
            x4 - 10,
            x2 + x4 - 0.35 * budget,
        ],
        dtype=float,
    )
    return np.round(np.maximum(slack, 0.0), 6)


def allocation_table(result: dict) -> pd.DataFrame:
    """Return a display-ready allocation table."""
    return pd.DataFrame(
        {
            "item": ["Hạ tầng số", "AI và dữ liệu", "Nhân lực số", "R&D công nghệ"],
            "symbol": ["x1", "x2", "x3", "x4"],
            "allocation": result["allocation"],
            "gdp_multiplier": [0.85, 1.20, 0.95, 1.35],
        }
    )


def constraint_table(result: dict) -> pd.DataFrame:
    """Return slack and shadow-price diagnostics for LP constraints."""
    names = [
        "Ngân sách tổng",
        "Hạ tầng số tối thiểu",
        "AI và dữ liệu tối thiểu",
        "Nhân lực số tối thiểu",
        "R&D tối thiểu",
        "Tỷ trọng AI + R&D >= 35%",
    ]
    shadow = result.get("shadow_prices")
    if shadow is None:
        shadow = [np.nan] * len(names)
    return pd.DataFrame(
        {
            "constraint": names,
            "sense": ["<=", ">=", ">=", ">=", ">=", ">="],
            "slack_or_surplus": result["slack"],
            "shadow_price": shadow,
        }
    )


def sensitivity_by_budget(
    budgets: list[float] | np.ndarray = (100.0, 120.0, 140.0),
    min_human: float = 20.0,
) -> pd.DataFrame:
    """Solve the LP over multiple budget levels."""
    rows = []
    for budget in budgets:
        result = solve_simple_budget_lp(float(budget), min_human=min_human)
        if result["success"]:
            row = {
                "budget": float(budget),
                "objective": result["objective"],
                "x1_infra": result["allocation"][0],
                "x2_ai_data": result["allocation"][1],
                "x3_human": result["allocation"][2],
                "x4_rd": result["allocation"][3],
            }
        else:
            row = {"budget": float(budget), "objective": np.nan}
        rows.append(row)
    return pd.DataFrame(rows)
