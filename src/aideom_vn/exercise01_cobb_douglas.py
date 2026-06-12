"""Exercise 1: extended Cobb-Douglas production model."""

from __future__ import annotations

import numpy as np
import pandas as pd


DEFAULT_PARAMS = {
    "alpha": 0.33,
    "beta": 0.42,
    "gamma": 0.10,
    "delta": 0.08,
    "theta": 0.07,
}

REFERENCE_INPUTS = pd.DataFrame(
    {
        "year": [2020, 2021, 2022, 2023, 2024, 2025],
        "K": [16500, 17800, 19600, 21300, 23500, 25900],
        "L": [53.6, 50.5, 51.7, 52.4, 52.9, 53.4],
        "AI": [55.6, 60.2, 65.4, 67.0, 73.8, 80.1],
        "H": [24.1, 26.1, 26.2, 27.0, 28.4, 29.2],
    }
)


def estimate_tfp(
    y: np.ndarray,
    k: np.ndarray,
    l: np.ndarray,
    d: np.ndarray,
    ai: np.ndarray,
    h: np.ndarray,
    params: dict[str, float] | None = None,
) -> np.ndarray:
    """Estimate TFP A_t from the extended Cobb-Douglas equation."""
    p = DEFAULT_PARAMS if params is None else params
    return y / (
        k ** p["alpha"]
        * l ** p["beta"]
        * d ** p["gamma"]
        * ai ** p["delta"]
        * h ** p["theta"]
    )


def mape(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Mean absolute percentage error in percent."""
    return float(np.mean(np.abs((actual - predicted) / actual)) * 100)


def complete_macro_inputs(df: pd.DataFrame) -> pd.DataFrame:
    """Attach the K/L/AI/H inputs from the exercise brief to macro data."""
    result = df.merge(REFERENCE_INPUTS, on="year", how="left")
    result = result.rename(
        columns={
            "GDP_trillion_VND": "Y",
            "digital_economy_share_GDP_pct": "D",
        }
    )
    missing = result[["K", "L", "D", "AI", "H", "Y"]].isna().any(axis=None)
    if missing:
        raise ValueError("Macro data is missing required Cobb-Douglas inputs.")
    return result


def predict_output(
    a: float,
    k: np.ndarray,
    l: np.ndarray,
    d: np.ndarray,
    ai: np.ndarray,
    h: np.ndarray,
    params: dict[str, float] | None = None,
) -> np.ndarray:
    """Predict output from fixed TFP and Cobb-Douglas inputs."""
    p = DEFAULT_PARAMS if params is None else params
    return a * (
        k ** p["alpha"]
        * l ** p["beta"]
        * d ** p["gamma"]
        * ai ** p["delta"]
        * h ** p["theta"]
    )


def run_cobb_douglas(
    macro_df: pd.DataFrame, params: dict[str, float] | None = None
) -> tuple[pd.DataFrame, dict[str, float]]:
    """Compute TFP, predicted GDP, and headline diagnostics."""
    p = DEFAULT_PARAMS if params is None else params
    df = complete_macro_inputs(macro_df).copy()
    df["TFP_A_t"] = estimate_tfp(
        df["Y"].to_numpy(),
        df["K"].to_numpy(),
        df["L"].to_numpy(),
        df["D"].to_numpy(),
        df["AI"].to_numpy(),
        df["H"].to_numpy(),
        p,
    )
    a_bar = float(df["TFP_A_t"].mean())
    df["Y_hat"] = predict_output(
        a_bar,
        df["K"].to_numpy(),
        df["L"].to_numpy(),
        df["D"].to_numpy(),
        df["AI"].to_numpy(),
        df["H"].to_numpy(),
        p,
    )
    df["abs_pct_error"] = (df["Y"] - df["Y_hat"]).abs() / df["Y"] * 100
    metrics = {
        "a_bar": a_bar,
        "mape": mape(df["Y"].to_numpy(), df["Y_hat"].to_numpy()),
        "tfp_growth_pct": (df["TFP_A_t"].iloc[-1] / df["TFP_A_t"].iloc[0] - 1)
        * 100,
    }
    return df, metrics


def growth_contribution(
    df: pd.DataFrame, params: dict[str, float] | None = None
) -> pd.DataFrame:
    """Return average annual log-growth contribution by input."""
    p = DEFAULT_PARAMS if params is None else params
    required = ["Y", "K", "L", "D", "AI", "H", "TFP_A_t"]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Missing columns for growth accounting: {missing}")

    mapping = {
        "TFP": ("TFP_A_t", 1.0),
        "Von vat chat K": ("K", p["alpha"]),
        "Lao dong L": ("L", p["beta"]),
        "So hoa D": ("D", p["gamma"]),
        "Nang luc AI": ("AI", p["delta"]),
        "Nhan luc so H": ("H", p["theta"]),
    }
    rows = []
    total_growth = float(np.log(df["Y"].iloc[-1] / df["Y"].iloc[0]))
    periods = len(df) - 1
    for name, (column, weight) in mapping.items():
        contribution = float(weight * np.log(df[column].iloc[-1] / df[column].iloc[0]))
        rows.append(
            {
                "factor": name,
                "log_contribution_total": contribution,
                "avg_annual_pct_point": contribution / periods * 100,
                "share_of_growth_pct": contribution / total_growth * 100,
            }
        )
    return pd.DataFrame(rows)


def forecast_2030(
    df: pd.DataFrame,
    metrics: dict[str, float],
    params: dict[str, float] | None = None,
    digital_share: float = 30.0,
    ai_firms: float = 100.0,
    human_capital: float = 35.0,
    k_growth: float = 6.0,
    l_growth: float = 0.6,
    tfp_growth: float = 1.2,
) -> dict[str, float]:
    """Forecast 2030 GDP under the scenario described in the exercise."""
    p = DEFAULT_PARAMS if params is None else params
    last = df.sort_values("year").iloc[-1]
    horizon = 2030 - int(last["year"])
    k_2030 = float(last["K"] * (1 + k_growth / 100) ** horizon)
    l_2030 = float(last["L"] * (1 + l_growth / 100) ** horizon)
    a_2030 = float(metrics["a_bar"] * (1 + tfp_growth / 100) ** horizon)
    y_2030 = float(
        predict_output(
            a_2030,
            np.array([k_2030]),
            np.array([l_2030]),
            np.array([digital_share]),
            np.array([ai_firms]),
            np.array([human_capital]),
            p,
        )[0]
    )
    return {
        "year": 2030,
        "GDP_2030_trillion_VND": y_2030,
        "K_2030": k_2030,
        "L_2030": l_2030,
        "D_2030": digital_share,
        "AI_2030": ai_firms,
        "H_2030": human_capital,
        "A_2030": a_2030,
    }
