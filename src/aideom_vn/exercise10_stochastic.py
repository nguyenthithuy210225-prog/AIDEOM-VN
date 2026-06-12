"""Exercise 10: two-stage stochastic planning.

The primary implementation uses Pyomo with a continuous first-stage policy
and scenario-specific recourse variables. A deterministic grid-search fallback
is kept for environments without an available Pyomo solver.
"""

from __future__ import annotations

from itertools import product

import numpy as np
import pandas as pd


SCENARIOS = pd.DataFrame(
    [
        ("Lạc quan", 0.25, 1.18, 1.12, 0.88),
        ("Cơ sở", 0.50, 1.00, 1.00, 1.00),
        ("Bi quan", 0.25, 0.78, 0.82, 1.28),
    ],
    columns=["scenario", "probability", "demand_factor", "fdi_factor", "risk_factor"],
)

MIN_SHARE = 0.10
MAX_SHARE = 0.70
MAX_AI_SHARE = 0.50
MIN_HUMAN_SHARE = 0.15


def evaluate_policy(shares: dict[str, float], budget: float = 80_000.0, scenarios: pd.DataFrame = SCENARIOS) -> pd.DataFrame:
    """Evaluate first-stage shares under each scenario with simple recourse."""
    rows = []
    for _, sc in scenarios.iterrows():
        k = shares["K"] * budget
        d = shares["D"] * budget
        ai = shares["AI"] * budget
        h = shares["H"] * budget
        recourse = max(0.0, 1.0 - sc["demand_factor"]) * 0.08 * budget
        gain = (
            0.76 * k
            + 1.05 * d * sc["demand_factor"]
            + 1.28 * ai * sc["fdi_factor"]
            + 0.98 * h
            - 0.18 * ai * sc["risk_factor"]
            - recourse
        )
        rows.append({"scenario": sc["scenario"], "probability": sc["probability"], "recourse_cost": recourse, "value": gain})
    return pd.DataFrame(rows)


def solve_stochastic_policy(budget: float = 80_000.0) -> dict:
    """Solve stochastic, expected-value, and wait-and-see models."""
    try:
        return _solve_stochastic_pyomo(budget)
    except Exception:
        return _solve_stochastic_grid(budget)


def _solve_stochastic_pyomo(budget: float = 80_000.0) -> dict:
    import pyomo.environ as pyo

    def solve_for_scenarios(scenarios: pd.DataFrame, objective_prob: bool = True) -> dict:
        model = pyo.ConcreteModel()
        items = ["K", "D", "AI", "H"]
        scen_ids = list(scenarios.index)
        model.I = pyo.Set(initialize=items)
        model.S = pyo.Set(initialize=scen_ids)
        model.x = pyo.Var(model.I, bounds=(MIN_SHARE, MAX_SHARE))
        model.recourse = pyo.Var(model.S, within=pyo.NonNegativeReals)
        model.share_sum = pyo.Constraint(expr=sum(model.x[i] for i in model.I) == 1.0)
        model.ai_absorption_cap = pyo.Constraint(expr=model.x["AI"] <= MAX_AI_SHARE)
        model.human_absorption_floor = pyo.Constraint(expr=model.x["H"] >= MIN_HUMAN_SHARE)

        def recourse_rule(m, s):
            demand = float(scenarios.loc[s, "demand_factor"])
            required = max(0.0, 1.0 - demand) * 0.08 * budget
            return m.recourse[s] >= required

        model.recourse_need = pyo.Constraint(model.S, rule=recourse_rule)

        def scenario_value(m, s):
            row = scenarios.loc[s]
            k = m.x["K"] * budget
            d = m.x["D"] * budget
            ai = m.x["AI"] * budget
            h = m.x["H"] * budget
            return (
                0.76 * k
                + 1.05 * d * float(row["demand_factor"])
                + 1.28 * ai * float(row["fdi_factor"])
                + 0.98 * h
                - 0.18 * ai * float(row["risk_factor"])
                - m.recourse[s]
            )

        if objective_prob:
            model.objective = pyo.Objective(
                expr=sum(float(scenarios.loc[s, "probability"]) * scenario_value(model, s) for s in model.S),
                sense=pyo.maximize,
            )
        else:
            s0 = scen_ids[0]
            model.objective = pyo.Objective(expr=scenario_value(model, s0), sense=pyo.maximize)

        solver = pyo.SolverFactory("appsi_highs")
        result = solver.solve(model)
        status = str(result.solver.termination_condition).lower()
        if "optimal" not in status:
            raise RuntimeError(f"Pyomo solver did not find optimum: {status}")
        shares = {i: float(pyo.value(model.x[i])) for i in items}
        expected = float(pyo.value(model.objective))
        return {"expected_value": expected, **shares}

    stochastic = solve_for_scenarios(SCENARIOS, objective_prob=True)
    base = SCENARIOS.iloc[[1]].copy()
    ev_policy = solve_for_scenarios(base, objective_prob=False)
    ev_eval = evaluate_policy({k: ev_policy[k] for k in ["K", "D", "AI", "H"]}, budget)
    ev_value = float((ev_eval["probability"] * ev_eval["value"]).sum())

    wait_values = []
    for _, sc in SCENARIOS.iterrows():
        single = pd.DataFrame([sc]).reset_index(drop=True)
        best = solve_for_scenarios(single, objective_prob=False)
        wait_values.append(best["expected_value"] * float(sc["probability"]))
    wait_see = float(sum(wait_values))

    grid_table = _policy_grid_table(budget)
    top = pd.DataFrame([stochastic]).assign(solver="pyomo.appsi_highs")
    policy_df = pd.concat([top, grid_table], ignore_index=True)
    policy_df = policy_df.drop_duplicates(["K", "D", "AI", "H"]).sort_values(
        "expected_value", ascending=False
    ).reset_index(drop=True)
    return {
        "policy_table": policy_df,
        "stochastic_policy": {**stochastic, "solver": "pyomo.appsi_highs"},
        "scenario_values": evaluate_policy({k: stochastic[k] for k in ["K", "D", "AI", "H"]}, budget),
        "ev_policy": ev_policy,
        "ev_value": ev_value,
        "vss": stochastic["expected_value"] - ev_value,
        "evpi": wait_see - stochastic["expected_value"],
        "solver": "pyomo.appsi_highs",
    }


def _policy_grid_table(budget: float = 80_000.0) -> pd.DataFrame:
    policies = []
    grid = np.arange(0.1, 0.71, 0.1)
    for k, d, ai in product(grid, repeat=3):
        h = 1 - k - d - ai
        if h < 0.1 or h > 0.7:
            continue
        shares = {"K": float(k), "D": float(d), "AI": float(ai), "H": float(h)}
        if shares["AI"] > MAX_AI_SHARE or shares["H"] < MIN_HUMAN_SHARE:
            continue
        evals = evaluate_policy(shares, budget)
        expected = float((evals["probability"] * evals["value"]).sum())
        policies.append({"expected_value": expected, **shares, "solver": "comparison_grid"})
    return pd.DataFrame(policies).sort_values("expected_value", ascending=False).reset_index(drop=True)


def _solve_stochastic_grid(budget: float = 80_000.0) -> dict:
    """Fallback solver compatible with the first project skeleton."""
    policies = []
    grid = np.arange(0.1, 0.71, 0.1)
    for k, d, ai in product(grid, repeat=3):
        h = 1 - k - d - ai
        if h < 0.1 or h > 0.7:
            continue
        shares = {"K": float(k), "D": float(d), "AI": float(ai), "H": float(h)}
        if shares["AI"] > MAX_AI_SHARE or shares["H"] < MIN_HUMAN_SHARE:
            continue
        evals = evaluate_policy(shares, budget)
        expected = float((evals["probability"] * evals["value"]).sum())
        policies.append({"expected_value": expected, **shares})
    policy_df = pd.DataFrame(policies).sort_values("expected_value", ascending=False).reset_index(drop=True)
    stochastic = policy_df.iloc[0].to_dict()

    base = SCENARIOS.iloc[[1]].copy()
    ev_rows = []
    for _, row in policy_df.iterrows():
        shares = {k: row[k] for k in ["K", "D", "AI", "H"]}
        ev_rows.append(evaluate_policy(shares, budget, base)["value"].iloc[0])
    ev_policy = policy_df.iloc[int(np.argmax(ev_rows))].to_dict()
    ev_eval = evaluate_policy({k: ev_policy[k] for k in ["K", "D", "AI", "H"]}, budget)
    ev_value = float((ev_eval["probability"] * ev_eval["value"]).sum())

    wait_values = []
    for _, sc in SCENARIOS.iterrows():
        best = max(
            evaluate_policy({k: row[k] for k in ["K", "D", "AI", "H"]}, budget, pd.DataFrame([sc]))["value"].iloc[0]
            for _, row in policy_df.iterrows()
        )
        wait_values.append(best * sc["probability"])
    wait_see = float(sum(wait_values))
    return {
        "policy_table": policy_df,
        "stochastic_policy": stochastic,
        "scenario_values": evaluate_policy({k: stochastic[k] for k in ["K", "D", "AI", "H"]}, budget),
        "ev_policy": ev_policy,
        "ev_value": ev_value,
        "vss": stochastic["expected_value"] - ev_value,
        "evpi": wait_see - stochastic["expected_value"],
    }
