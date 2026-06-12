"""Generate reproducible CSV outputs for all AIDEOM-VN exercises."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aideom_vn.config import TABLE_DIR, ensure_output_dirs
from aideom_vn.data_loader import load_macro, load_regions, load_sectors
from aideom_vn.exercise01_cobb_douglas import forecast_2030, growth_contribution, run_cobb_douglas
from aideom_vn.exercise02_lp_budget import allocation_table, constraint_table, sensitivity_by_budget, solve_simple_budget_lp
from aideom_vn.exercise03_priority import run_priority_model, sensitivity_top_sectors
from aideom_vn.exercise04_region_sector_lp import solve_region_sector_lp
from aideom_vn.exercise05_project_mip import solve_project_mip
from aideom_vn.exercise06_topsis import run_topsis
from aideom_vn.exercise07_pareto import run_pareto_search
from aideom_vn.exercise08_dynamic import optimize_dynamic_policy, simulate_dynamic_policy
from aideom_vn.exercise09_labor import find_training_threshold, simulate_labor_impact
from aideom_vn.exercise10_stochastic import solve_stochastic_policy
from aideom_vn.exercise11_qlearning import train_q_learning
from aideom_vn.exercise12_integrated import evaluate_scenarios, module_design_table


def save(df, name: str) -> None:
    path = TABLE_DIR / name
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(path)


def main() -> None:
    ensure_output_dirs()
    macro = load_macro()
    sectors = load_sectors()
    regions = load_regions()

    b1, b1_metrics = run_cobb_douglas(macro)
    save(b1, "bai01_cobb_douglas.csv")
    save(growth_contribution(b1), "bai01_growth_accounting.csv")
    save(pd.DataFrame([forecast_2030(b1, b1_metrics)]), "bai01_forecast_2030.csv")

    b2 = solve_simple_budget_lp()
    save(allocation_table(b2), "bai02_allocation.csv")
    save(constraint_table(b2), "bai02_constraints.csv")
    save(sensitivity_by_budget([100, 120, 140]), "bai02_sensitivity.csv")
    save(
        pd.DataFrame(
            [
                {
                    "solver": b2.get("solver"),
                    "shadow_price_source": b2.get("shadow_price_source"),
                    "objective": b2.get("objective"),
                    "message": b2.get("message"),
                }
            ]
        ),
        "bai02_solver_summary.csv",
    )

    b3, b3_norm = run_priority_model(sectors)
    save(b3, "bai03_priority.csv")
    save(b3_norm, "bai03_normalized.csv")
    save(sensitivity_top_sectors(sectors), "bai03_sensitivity.csv")

    b4 = solve_region_sector_lp(regions, sectors)
    save(b4["allocation"], "bai04_allocation.csv")
    save(b4["region_summary"], "bai04_region_summary.csv")
    save(b4["item_summary"], "bai04_item_summary.csv")

    b5 = solve_project_mip()
    save(b5["projects"], "bai05_projects.csv")
    save(b5["selected"], "bai05_selected_projects.csv")

    b6, b6_weights = run_topsis(regions)
    save(b6, "bai06_topsis.csv")
    save(b6_weights.reset_index().rename(columns={"index": "criterion", 0: "weight"}), "bai06_entropy_weights.csv")

    b7 = run_pareto_search(population=80, generations=80)
    save(b7["pareto"], "bai07_pareto.csv")
    save(pd.DataFrame([b7["compromise"]]), "bai07_compromise.csv")

    b8 = optimize_dynamic_policy(macro)
    save(b8["trajectory"], "bai08_dynamic_trajectory.csv")
    save(b8["ranking"].head(20), "bai08_policy_ranking.csv")
    if "plan" in b8:
        save(b8["plan"], "bai08_dynamic_plan.csv")
    save(
        simulate_dynamic_policy(macro, {"K": 0.30, "D": 0.25, "AI": 0.25, "H": 0.20}),
        "bai08_baseline_trajectory.csv",
    )

    b9 = simulate_labor_impact(sectors)
    save(b9, "bai09_labor_impact.csv")
    save(find_training_threshold(sectors)["result"], "bai09_threshold_result.csv")

    b10 = solve_stochastic_policy()
    save(b10["scenario_values"], "bai10_scenario_values.csv")
    save(b10["policy_table"].head(20), "bai10_policy_table.csv")
    save(
        pd.DataFrame(
            [
                {
                    "solver": b10.get("solver"),
                    "vss": b10["vss"],
                    "evpi": b10["evpi"],
                    "interpretation": "VSS = 0 means the expected-value policy matches the stochastic policy under current parameters; EVPI > 0 means perfect scenario information still has value.",
                }
            ]
        ),
        "bai10_value_of_information.csv",
    )

    b11 = train_q_learning()
    save(b11["q_table"].reset_index().rename(columns={"index": "state"}), "bai11_q_table.csv")
    save(b11["policy"], "bai11_policy.csv")
    save(b11["reward_trace"], "bai11_reward_trace.csv")

    save(evaluate_scenarios(sectors), "bai12_scenarios.csv")
    save(module_design_table(), "bai12_module_design.csv")


if __name__ == "__main__":
    main()
