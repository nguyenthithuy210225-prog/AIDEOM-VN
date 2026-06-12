"""Exercise 8: formal intertemporal allocation for 2026-2035."""

from __future__ import annotations

from itertools import product

import numpy as np
import pandas as pd

from .exercise01_cobb_douglas import complete_macro_inputs, predict_output

MIN_SHARE = 0.10
MAX_SHARE = 0.60
DISCOUNT_RATE = 0.04
AI_POLICY_PENALTY = 1200.0
HUMAN_POLICY_BONUS = 500.0


def simulate_dynamic_policy(
    macro: pd.DataFrame,
    shares: dict[str, float],
    annual_budget: float = 650.0,
    start_year: int = 2026,
    end_year: int = 2035,
) -> pd.DataFrame:
    """Simulate GDP path under fixed K/D/AI/H allocation shares."""
    base = complete_macro_inputs(macro).sort_values("year").iloc[-1]
    state = {
        "K": float(base["K"]),
        "L": float(base["L"]),
        "D": float(base["D"]),
        "AI": float(base["AI"]),
        "H": float(base["H"]),
        "A": 1.012 * 35.5,
    }
    rows = []
    for year in range(start_year, end_year + 1):
        invest_k = annual_budget * shares["K"]
        invest_d = annual_budget * shares["D"]
        invest_ai = annual_budget * shares["AI"]
        invest_h = annual_budget * shares["H"]
        state["K"] = state["K"] * 1.045 + invest_k * 3.8
        state["L"] = state["L"] * 1.006
        state["D"] = min(38.0, state["D"] + invest_d / 850 + 0.20)
        state["AI"] = min(145.0, state["AI"] + invest_ai / 470 + 1.5)
        state["H"] = min(43.0, state["H"] + invest_h / 900 + 0.25)
        state["A"] *= 1.012 + 0.002 * shares["D"] + 0.0015 * shares["AI"]
        y = predict_output(
            state["A"],
            np.array([state["K"]]),
            np.array([state["L"]]),
            np.array([state["D"]]),
            np.array([state["AI"]]),
            np.array([state["H"]]),
        )[0]
        rows.append({"year": year, "GDP": y, **state, **{f"share_{k}": v for k, v in shares.items()}})
    return pd.DataFrame(rows)


def simulate_dynamic_plan(
    macro: pd.DataFrame,
    plan: pd.DataFrame,
    annual_budget: float = 650.0,
) -> pd.DataFrame:
    """Simulate GDP path under year-specific K/D/AI/H shares."""
    rows = []
    current = complete_macro_inputs(macro).sort_values("year").iloc[-1]
    state = {
        "K": float(current["K"]),
        "L": float(current["L"]),
        "D": float(current["D"]),
        "AI": float(current["AI"]),
        "H": float(current["H"]),
        "A": 1.012 * 35.5,
    }
    for _, row in plan.sort_values("year").iterrows():
        shares = {key: float(row[key]) for key in ["K", "D", "AI", "H"]}
        state["K"] = state["K"] * 1.045 + annual_budget * shares["K"] * 3.8
        state["L"] = state["L"] * 1.006
        state["D"] = min(38.0, state["D"] + annual_budget * shares["D"] / 850 + 0.20)
        state["AI"] = min(145.0, state["AI"] + annual_budget * shares["AI"] / 470 + 1.5)
        state["H"] = min(43.0, state["H"] + annual_budget * shares["H"] / 900 + 0.25)
        state["A"] *= 1.012 + 0.002 * shares["D"] + 0.0015 * shares["AI"]
        y = predict_output(
            state["A"],
            np.array([state["K"]]),
            np.array([state["L"]]),
            np.array([state["D"]]),
            np.array([state["AI"]]),
            np.array([state["H"]]),
        )[0]
        rows.append({"year": int(row["year"]), "GDP": y, **state, **{f"share_{k}": v for k, v in shares.items()}})
    return pd.DataFrame(rows)


def optimize_dynamic_policy(macro: pd.DataFrame, annual_budget: float = 650.0) -> dict:
    """Solve a formal intertemporal program, with grid fallback."""
    try:
        return _optimize_dynamic_cvxpy(macro, annual_budget)
    except Exception:
        try:
            return _optimize_dynamic_slsqp(macro, annual_budget)
        except Exception:
            return _optimize_dynamic_grid(macro, annual_budget)


def _trajectory_score(path: pd.DataFrame) -> float:
    discount = np.array([1 / ((1 + DISCOUNT_RATE) ** i) for i in range(len(path))])
    ai_penalty = AI_POLICY_PENALTY * float(path["share_AI"].mean())
    human_bonus = HUMAN_POLICY_BONUS * float(path["share_H"].mean())
    return float(np.dot(path["GDP"], discount) - ai_penalty + human_bonus)


def _optimize_dynamic_cvxpy(macro: pd.DataFrame, annual_budget: float = 650.0) -> dict:
    """Optimize annual investment shares with a convex log-Cobb-Douglas model."""
    import cvxpy as cp

    start_year = 2026
    end_year = 2035
    years = list(range(start_year, end_year + 1))
    horizon = len(years)
    base = complete_macro_inputs(macro).sort_values("year").iloc[-1]

    shares = cp.Variable((horizon, 4), name="shares")
    k_state = cp.Variable(horizon, name="K")
    d_state = cp.Variable(horizon, name="D")
    ai_state = cp.Variable(horizon, name="AI")
    h_state = cp.Variable(horizon, name="H")
    log_a = cp.Variable(horizon, name="log_A")

    constraints = [
        shares >= MIN_SHARE,
        shares <= MAX_SHARE,
        cp.sum(shares, axis=1) == 1,
        k_state >= 1,
        d_state >= 1,
        ai_state >= 1,
        h_state >= 1,
        d_state <= 38.0,
        ai_state <= 145.0,
        h_state <= 43.0,
    ]
    for t in range(horizon):
        prev_k = float(base["K"]) if t == 0 else k_state[t - 1]
        prev_d = float(base["D"]) if t == 0 else d_state[t - 1]
        prev_ai = float(base["AI"]) if t == 0 else ai_state[t - 1]
        prev_h = float(base["H"]) if t == 0 else h_state[t - 1]
        prev_log_a = np.log(1.012 * 35.5) if t == 0 else log_a[t - 1]

        constraints += [
            k_state[t] == prev_k * 1.045 + annual_budget * shares[t, 0] * 3.8,
            d_state[t] <= prev_d + annual_budget * shares[t, 1] / 850 + 0.20,
            ai_state[t] <= prev_ai + annual_budget * shares[t, 2] / 470 + 1.5,
            h_state[t] <= prev_h + annual_budget * shares[t, 3] / 900 + 0.25,
            log_a[t] == prev_log_a + np.log(1.012) + 0.002 * shares[t, 1] + 0.0015 * shares[t, 2],
        ]

    labor_path = np.array([float(base["L"]) * (1.006 ** (i + 1)) for i in range(horizon)])
    discount = np.array([1 / ((1 + DISCOUNT_RATE) ** i) for i in range(horizon)])
    log_gdp = (
        log_a
        + 0.33 * cp.log(k_state)
        + 0.42 * np.log(labor_path)
        + 0.10 * cp.log(d_state)
        + 0.08 * cp.log(ai_state)
        + 0.07 * cp.log(h_state)
    )
    objective = cp.Maximize(
        cp.sum(cp.multiply(discount, log_gdp))
        - 0.015 * cp.sum(shares[:, 2])
        + 0.006 * cp.sum(shares[:, 3])
        - 0.004 * cp.sum_squares(shares[1:, :] - shares[:-1, :])
    )
    problem = cp.Problem(objective, constraints)
    for solver in ("CLARABEL", "ECOS", "SCS"):
        if solver in cp.installed_solvers():
            problem.solve(solver=solver, verbose=False)
            if problem.status in {cp.OPTIMAL, cp.OPTIMAL_INACCURATE}:
                break
    if problem.status not in {cp.OPTIMAL, cp.OPTIMAL_INACCURATE}:
        raise RuntimeError(f"CVXPY did not solve dynamic model: {problem.status}")

    plan = pd.DataFrame(shares.value, columns=["K", "D", "AI", "H"])
    plan["year"] = years
    plan = plan[["year", "K", "D", "AI", "H"]]
    trajectory = simulate_dynamic_plan(macro, plan, annual_budget)
    avg_shares = {item: float(plan[item].mean()) for item in ["K", "D", "AI", "H"]}
    best = {
        "score": _trajectory_score(trajectory),
        **avg_shares,
        "GDP_2035": float(trajectory["GDP"].iloc[-1]),
        "solver": f"CVXPY_{problem.solver_stats.solver_name}",
        "objective_type": "discounted_log_Cobb_Douglas",
    }
    ranking = plan.copy()
    ranking["score"] = np.nan
    ranking["GDP_2035"] = np.nan
    ranking.loc[ranking.index[-1], "GDP_2035"] = best["GDP_2035"]
    return {"best": best, "ranking": ranking, "trajectory": trajectory, "plan": plan, "solver": best["solver"]}


def _optimize_dynamic_slsqp(macro: pd.DataFrame, annual_budget: float = 650.0) -> dict:
    """Optimize year-by-year shares as a constrained nonlinear program."""
    from scipy.optimize import minimize

    years = list(range(2026, 2036))
    horizon = len(years)
    initial_share = np.array([0.30, 0.25, 0.25, 0.20])
    x0 = np.tile(initial_share, horizon)
    bounds = [(MIN_SHARE, MAX_SHARE)] * (horizon * 4)
    constraints = [
        {
            "type": "eq",
            "fun": lambda x, t=t: float(np.sum(x.reshape(horizon, 4)[t]) - 1.0),
        }
        for t in range(horizon)
    ]

    def to_plan(x: np.ndarray) -> pd.DataFrame:
        plan = pd.DataFrame(x.reshape(horizon, 4), columns=["K", "D", "AI", "H"])
        plan["year"] = years
        return plan[["year", "K", "D", "AI", "H"]]

    def objective(x: np.ndarray) -> float:
        path = simulate_dynamic_plan(macro, to_plan(x), annual_budget)
        return -_trajectory_score(path)

    result = minimize(
        objective,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 500, "ftol": 1e-7, "disp": False},
    )
    share_matrix = result.x.reshape(horizon, 4)
    max_sum_error = float(np.max(np.abs(share_matrix.sum(axis=1) - 1.0)))
    bounds_ok = bool(share_matrix.min() >= MIN_SHARE - 1e-5 and share_matrix.max() <= MAX_SHARE + 1e-5)
    if not result.success and (max_sum_error > 1e-5 or not bounds_ok):
        raise RuntimeError(result.message)

    share_matrix = np.clip(share_matrix, MIN_SHARE, MAX_SHARE)
    share_matrix = share_matrix / share_matrix.sum(axis=1, keepdims=True)
    plan = to_plan(share_matrix.ravel())
    trajectory = simulate_dynamic_plan(macro, plan, annual_budget)
    avg_shares = {item: float(plan[item].mean()) for item in ["K", "D", "AI", "H"]}
    best = {
        "score": _trajectory_score(trajectory),
        **avg_shares,
        "GDP_2035": float(trajectory["GDP"].iloc[-1]),
        "solver": "scipy.SLSQP_intertemporal_NLP",
        "objective_type": "discounted_Cobb_Douglas_path",
    }
    ranking = plan.copy()
    ranking["score"] = np.nan
    ranking["GDP_2035"] = np.nan
    ranking.loc[ranking.index[-1], "GDP_2035"] = best["GDP_2035"]
    return {"best": best, "ranking": ranking, "trajectory": trajectory, "plan": plan, "solver": best["solver"]}


def _optimize_dynamic_grid(macro: pd.DataFrame, annual_budget: float = 650.0) -> dict:
    """Search a coarse grid of fixed policy shares when CVXPY is unavailable."""
    candidates = []
    grid = np.arange(MIN_SHARE, MAX_SHARE + 0.01, 0.1)
    for k, d, ai in product(grid, repeat=3):
        h = 1 - k - d - ai
        if h < MIN_SHARE or h > MAX_SHARE:
            continue
        shares = {"K": float(k), "D": float(d), "AI": float(ai), "H": float(h)}
        path = simulate_dynamic_policy(macro, shares, annual_budget=annual_budget)
        score = _trajectory_score(path)
        candidates.append({"score": score, **shares, "GDP_2035": path["GDP"].iloc[-1]})
    ranking = pd.DataFrame(candidates).sort_values("score", ascending=False).reset_index(drop=True)
    best = ranking.iloc[0].to_dict()
    best_path = simulate_dynamic_policy(macro, {k: best[k] for k in ["K", "D", "AI", "H"]}, annual_budget)
    best["solver"] = "fixed_share_grid_fallback"
    return {"best": best, "ranking": ranking, "trajectory": best_path, "solver": best["solver"]}
