from aideom_vn.data_loader import load_macro, load_regions, load_sectors
from aideom_vn.exercise01_cobb_douglas import forecast_2030, run_cobb_douglas
from aideom_vn.exercise04_region_sector_lp import solve_region_sector_lp
from aideom_vn.exercise05_project_mip import solve_project_mip
from aideom_vn.exercise06_topsis import run_topsis
from aideom_vn.exercise07_pareto import run_pareto_search
from aideom_vn.exercise08_dynamic import optimize_dynamic_policy
from aideom_vn.exercise09_labor import find_training_threshold, simulate_labor_impact
from aideom_vn.exercise10_stochastic import solve_stochastic_policy
from aideom_vn.exercise11_qlearning import train_q_learning
from aideom_vn.exercise12_integrated import evaluate_scenarios


def test_mid_level_models_run():
    sectors = load_sectors()
    regions = load_regions()
    assert solve_region_sector_lp(regions, sectors)["success"]
    assert solve_project_mip()["success"]
    ranking, weights = run_topsis(regions)
    assert len(ranking) == 6
    assert round(weights.sum(), 6) == 1


def test_advanced_models_run():
    macro = load_macro()
    sectors = load_sectors()
    pareto = run_pareto_search(population=20, generations=10)
    assert len(pareto["pareto"]) > 0
    assert optimize_dynamic_policy(macro)["trajectory"]["GDP"].iloc[-1] > 0
    assert simulate_labor_impact(sectors)["net_job_million"].notna().all()
    assert find_training_threshold(sectors)["threshold"] >= 0
    assert "vss" in solve_stochastic_policy()
    assert len(train_q_learning(episodes=20)["policy"]) == 4
    assert len(evaluate_scenarios(sectors)) == 6


def test_forecast_2030_uses_plausible_labor_growth():
    macro = load_macro()
    result, metrics = run_cobb_douglas(macro)
    forecast = forecast_2030(result, metrics)
    assert 54.0 <= forecast["L_2030"] <= 57.0


def test_stochastic_policy_has_absorption_bounds():
    policy = solve_stochastic_policy()["stochastic_policy"]
    assert policy["AI"] <= 0.500001
    assert policy["H"] >= 0.149999


def test_integrated_reskilling_scenario_has_positive_netjob():
    scenarios = evaluate_scenarios(load_sectors())
    reskilling = scenarios[scenarios["scenario"].str.contains("Reskilling")].iloc[0]
    assert reskilling["net_job_million"] > 0
