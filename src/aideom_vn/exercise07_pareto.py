"""Exercise 7: Pareto multi-objective search for policy portfolios.

The primary solver is pymoo NSGA-II, matching the coursework requirement.
The previous stochastic evolutionary search is kept as a fallback so the
dashboard remains runnable on machines without pymoo.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _nondominated(df: pd.DataFrame) -> pd.DataFrame:
    values = df[["gdp_gain", "inclusion", "green_score", "data_security"]].to_numpy()
    keep = np.ones(len(df), dtype=bool)
    for i, vi in enumerate(values):
        if not keep[i]:
            continue
        dominates_i = (
            (values >= vi).all(axis=1)
            & (values > vi).any(axis=1)
        )
        if dominates_i.any():
            keep[i] = False
    return df[keep].copy()


def run_pareto_search(
    budget: float = 80_000.0,
    population: int = 80,
    generations: int = 80,
    seed: int = 42,
) -> dict:
    """Run NSGA-II over K/D/AI/H shares and return Pareto solutions."""
    try:
        return _run_pymoo_nsga2(budget, population, generations, seed)
    except Exception:
        return _run_fallback_search(budget, population, generations, seed)


def _run_pymoo_nsga2(
    budget: float,
    population: int,
    generations: int,
    seed: int,
) -> dict:
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.core.problem import ElementwiseProblem
    from pymoo.optimize import minimize
    from pymoo.termination import get_termination

    class PolicyPortfolioProblem(ElementwiseProblem):
        def __init__(self) -> None:
            super().__init__(
                n_var=3,
                n_obj=4,
                n_ieq_constr=2,
                xl=np.array([0.1, 0.1, 0.1]),
                xu=np.array([0.7, 0.7, 0.7]),
            )

        def _evaluate(self, x, out, *args, **kwargs) -> None:
            k, d, ai = x
            h = 1.0 - k - d - ai
            shares = np.array([[k, d, ai, max(h, 0.1)]], dtype=float)
            scores = _score_allocations(shares, budget).iloc[0]
            out["F"] = [
                -scores["gdp_gain"],
                -scores["inclusion"],
                -scores["green_score"],
                -scores["data_security"],
            ]
            out["G"] = [k + d + ai - 0.9, 0.3 - k - d - ai]

    algorithm = NSGA2(pop_size=max(20, int(population)))
    result = minimize(
        PolicyPortfolioProblem(),
        algorithm,
        get_termination("n_gen", max(1, int(generations))),
        seed=seed,
        verbose=False,
    )
    x = np.asarray(result.X, dtype=float)
    if x.ndim == 1:
        x = x.reshape(1, -1)
    shares = np.column_stack([x[:, 0], x[:, 1], x[:, 2], 1.0 - x.sum(axis=1)])
    shares = np.maximum(shares, 0.1)
    shares = shares / shares.sum(axis=1, keepdims=True)
    solutions = _score_allocations(shares, budget).drop_duplicates(
        ["K_share", "D_share", "AI_share", "H_share"]
    )
    pareto = _nondominated(solutions).sort_values("gdp_gain", ascending=False).reset_index(drop=True)
    compromise = choose_compromise(pareto)
    compromise["solver"] = "pymoo.NSGA2"
    return {"solutions": solutions, "pareto": pareto, "compromise": compromise, "solver": "pymoo.NSGA2"}


def _run_fallback_search(
    budget: float,
    population: int,
    generations: int,
    seed: int,
) -> dict:
    """Run a light evolutionary fallback over K/D/AI/H shares."""
    rng = np.random.default_rng(seed)
    samples = []
    current = _sample_feasible_shares(rng, population)
    for _ in range(generations):
        noise = rng.normal(0, 0.055, size=current.shape)
        children = np.maximum(current + noise, 0.1)
        children = children / children.sum(axis=1, keepdims=True)
        children = _repair_shares(children)
        mixed = np.vstack([current, children, _sample_feasible_shares(rng, population // 2)])
        temp = _score_allocations(mixed, budget)
        survivors = _nondominated(temp)
        if len(survivors) < population:
            extra = temp.sort_values("gdp_gain", ascending=False).head(population - len(survivors))
            survivors = pd.concat([survivors, extra], ignore_index=True)
        current = survivors[["K_share", "D_share", "AI_share", "H_share"]].head(population).to_numpy()
        samples.append(temp)
    all_solutions = pd.concat(samples, ignore_index=True).drop_duplicates(
        ["K_share", "D_share", "AI_share", "H_share"]
    )
    pareto = _nondominated(all_solutions).sort_values("gdp_gain", ascending=False).reset_index(drop=True)
    compromise = choose_compromise(pareto)
    compromise["solver"] = "fallback_evolutionary_search"
    return {
        "solutions": all_solutions,
        "pareto": pareto,
        "compromise": compromise,
        "solver": "fallback_evolutionary_search",
    }


def _sample_feasible_shares(rng: np.random.Generator, n: int) -> np.ndarray:
    """Sample K/D/AI/H shares with each item between 10% and 70%."""
    raw = rng.dirichlet(np.ones(4), size=max(1, n))
    return _repair_shares(raw)


def _repair_shares(shares: np.ndarray) -> np.ndarray:
    shares = np.clip(shares, 0.1, 0.7)
    for _ in range(20):
        shares = shares / shares.sum(axis=1, keepdims=True)
        low = shares < 0.1
        high = shares > 0.7
        if not (low.any() or high.any()):
            break
        shares = np.clip(shares, 0.1, 0.7)
    return shares / shares.sum(axis=1, keepdims=True)


def _score_allocations(shares: np.ndarray, budget: float) -> pd.DataFrame:
    k, d, ai, h = shares.T
    df = pd.DataFrame({"K_share": k, "D_share": d, "AI_share": ai, "H_share": h})
    df["K"] = df["K_share"] * budget
    df["D"] = df["D_share"] * budget
    df["AI"] = df["AI_share"] * budget
    df["H"] = df["H_share"] * budget
    df["gdp_gain"] = 0.75 * df["K"] + 1.05 * df["D"] + 1.35 * df["AI"] + 0.98 * df["H"]
    df["inclusion"] = 0.35 * df["K"] + 0.70 * df["D"] + 0.42 * df["AI"] + 1.18 * df["H"]
    df["green_score"] = 0.45 * df["K"] + 0.82 * df["D"] + 0.55 * df["AI"] + 0.78 * df["H"]
    df["data_security"] = 0.38 * df["K"] + 0.62 * df["D"] + 0.74 * df["AI"] + 0.58 * df["H"]
    df["risk_index"] = 0.16 * df["K_share"] + 0.22 * df["D_share"] + 0.42 * df["AI_share"] - 0.18 * df["H_share"]
    return df


def choose_compromise(pareto: pd.DataFrame) -> pd.Series:
    """Choose a balanced Pareto solution by normalized distance to the ideal."""
    cols = ["gdp_gain", "inclusion", "green_score", "data_security"]
    normalized = (pareto[cols] - pareto[cols].min()) / (pareto[cols].max() - pareto[cols].min() + 1e-12)
    concentration = ((pareto[["K_share", "D_share", "AI_share", "H_share"]] - 0.25) ** 2).sum(axis=1)
    pareto = pareto.copy()
    pareto["compromise_score"] = normalized.mean(axis=1) - pareto["risk_index"] * 0.20 - concentration * 0.25
    return pareto.sort_values("compromise_score", ascending=False).iloc[0]
