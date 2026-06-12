from aideom_vn.exercise02_lp_budget import constraint_table, solve_simple_budget_lp
from aideom_vn.exercise03_priority import minmax


def test_simple_budget_lp_solves():
    result = solve_simple_budget_lp()
    assert result["success"]
    assert round(sum(result["allocation"]), 6) <= 100.0
    assert result["solver"] == "PuLP_CBC"
    assert result["shadow_price_source"] == "PuLP/CBC constraint pi"
    constraints = constraint_table(result)
    assert (constraints["slack_or_surplus"] >= 0).all()


def test_minmax_bounds():
    values = minmax(__import__("pandas").Series([1, 2, 3]))
    assert values.min() == 0
    assert values.max() == 1
