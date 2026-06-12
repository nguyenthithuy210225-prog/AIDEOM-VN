from aideom_vn.data_loader import load_macro, load_regions, load_sectors
from aideom_vn.exercise01_cobb_douglas import forecast_2030, run_cobb_douglas
from aideom_vn.exercise02_lp_budget import allocation_table, constraint_table, solve_simple_budget_lp
from aideom_vn.exercise03_priority import DEFAULT_WEIGHTS, run_priority_model
from aideom_vn.exercise04_region_sector_lp import solve_region_sector_lp
from aideom_vn.exercise05_project_mip import PROJECTS, solve_project_mip
from aideom_vn.exercise06_topsis import run_topsis
from aideom_vn.exercise07_pareto import run_pareto_search
from aideom_vn.exercise08_dynamic import optimize_dynamic_policy, simulate_dynamic_policy
from aideom_vn.exercise09_labor import find_training_threshold, simulate_labor_impact
from aideom_vn.exercise10_stochastic import solve_stochastic_policy
from aideom_vn.exercise11_qlearning import train_q_learning
from aideom_vn.exercise12_integrated import evaluate_scenarios
from aideom_vn.policy_briefs import (
    bai01_brief,
    bai02_brief,
    bai03_brief,
    bai04_brief,
    bai05_brief,
    bai06_brief,
    bai07_brief,
    bai08_brief,
    bai09_brief,
    bai10_brief,
    bai11_brief,
    bai12_brief,
    home_brief,
)


def assert_valid_brief(sections):
    assert sections
    for title, points in sections:
        assert isinstance(title, str) and title
        assert isinstance(points, list) and points
        assert all(isinstance(point, str) and point for point in points)


def test_policy_brief_generators_run_on_model_outputs():
    macro = load_macro()
    sectors = load_sectors()
    regions = load_regions()

    assert_valid_brief(home_brief(macro, sectors, regions))

    cd_result, cd_metrics = run_cobb_douglas(macro)
    assert_valid_brief(bai01_brief(cd_result, cd_metrics, forecast_2030(cd_result, cd_metrics)))

    lp = solve_simple_budget_lp()
    lp["budget"] = 100.0
    assert_valid_brief(bai02_brief(lp, allocation_table(lp), constraint_table(lp)))

    ranked, _normalized = run_priority_model(sectors, DEFAULT_WEIGHTS)
    assert_valid_brief(bai03_brief(ranked, DEFAULT_WEIGHTS))

    assert_valid_brief(bai04_brief(solve_region_sector_lp(regions, sectors)))
    assert_valid_brief(bai05_brief(solve_project_mip(), len(PROJECTS), 80_000.0, 145.0))

    ranking, weights = run_topsis(regions)
    assert_valid_brief(bai06_brief(ranking, weights))

    assert_valid_brief(bai07_brief(run_pareto_search(population=20, generations=10)))

    dynamic = optimize_dynamic_policy(macro)
    baseline = simulate_dynamic_policy(macro, {"K": 0.30, "D": 0.25, "AI": 0.25, "H": 0.20})
    assert_valid_brief(bai08_brief(dynamic, baseline))

    labor = simulate_labor_impact(sectors)
    assert_valid_brief(bai09_brief(labor, find_training_threshold(sectors)))

    assert_valid_brief(bai10_brief(solve_stochastic_policy()))
    assert_valid_brief(bai11_brief(train_q_learning(episodes=20)))
    assert_valid_brief(bai12_brief(evaluate_scenarios(sectors)))
