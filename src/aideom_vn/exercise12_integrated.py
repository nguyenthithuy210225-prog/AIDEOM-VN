"""Exercise 12: integrated AIDEOM-VN scenario dashboard."""

from __future__ import annotations

import pandas as pd

from .exercise09_labor import simulate_labor_impact


SCENARIO_SHARES = pd.DataFrame(
    [
        ("S1. Truyen thong", 0.70, 0.10, 0.10, 0.10, 1.00),
        ("S2. So hoa nhanh", 0.25, 0.45, 0.15, 0.15, 1.00),
        ("S3. AI dan dat", 0.20, 0.20, 0.45, 0.15, 1.00),
        ("S4. Bao trum so", 0.30, 0.20, 0.10, 0.40, 1.00),
        ("S5. Toi uu can bang", 0.30, 0.25, 0.25, 0.20, 1.00),
        ("S6. Reskilling manh", 0.20, 0.15, 0.10, 0.55, 3.50),
    ],
    columns=["scenario", "K", "D", "AI", "H", "training_multiplier"],
)


def evaluate_scenarios(sectors: pd.DataFrame, budget: float = 80_000.0) -> pd.DataFrame:
    """Compute headline KPI table for six AIDEOM-VN policy scenarios."""
    rows = []
    for _, sc in SCENARIO_SHARES.iterrows():
        gdp_gain = budget * (0.78 * sc["K"] + 1.05 * sc["D"] + 1.32 * sc["AI"] + 0.98 * sc["H"])
        inclusion = budget * (0.40 * sc["K"] + 0.68 * sc["D"] + 0.45 * sc["AI"] + 1.15 * sc["H"])
        risk = 100 * (0.16 * sc["K"] + 0.22 * sc["D"] + 0.44 * sc["AI"] - 0.18 * sc["H"])
        labor = simulate_labor_impact(
            sectors,
            adoption_rate=0.38 + 0.22 * sc["AI"],
            training_budget=budget * sc["H"] * sc["training_multiplier"],
            ai_investment=budget * sc["AI"],
        )
        rows.append(
            {
                "scenario": sc["scenario"],
                "GDP_gain": gdp_gain,
                "inclusion": inclusion,
                "risk_index": risk,
                "net_job_million": labor["net_job_million"].sum(),
                "K": sc["K"],
                "D": sc["D"],
                "AI": sc["AI"],
                "H": sc["H"],
                "training_multiplier": sc["training_multiplier"],
            }
        )
    df = pd.DataFrame(rows)
    df["overall_score"] = (
        df["GDP_gain"].rank(pct=True)
        + df["inclusion"].rank(pct=True)
        + df["net_job_million"].rank(pct=True)
        + (1 - df["risk_index"].rank(pct=True))
    ) / 4
    return df.sort_values("overall_score", ascending=False).reset_index(drop=True)


def module_design_table() -> pd.DataFrame:
    """Return the six-module architecture table."""
    return pd.DataFrame(
        [
            ("M1", "Du bao kinh te", "Macro 2020-2025", "GDP, TFP 2030", "Cobb-Douglas"),
            ("M2", "San sang so", "Sectors, Regions", "Digital + AI Index", "TOPSIS"),
            ("M3", "Toi uu phan bo", "Budget, beta matrix", "Phan bo nganh-vung", "LP + dynamic"),
            ("M4", "Lao dong", "AI, H plans", "NetJob tung nganh", "Simulation"),
            ("M5", "Rui ro", "Risk params", "Cyber, env, dependency", "Pareto + SP"),
            ("M6", "Dashboard", "Outputs M1-M5", "Truc quan kich ban", "Streamlit + Plotly"),
        ],
        columns=["module", "name", "input", "output", "method"],
    )
