"""Exercise 5: project-selection MIP.

PuLP/CBC is the primary binary optimization solver. Exhaustive search is kept
as a transparent fallback and for counting feasible portfolios.
"""

from __future__ import annotations

from itertools import product

import numpy as np
import pandas as pd


PROJECTS = pd.DataFrame(
    [
        ("P01", "Nền tảng dữ liệu quốc gia", "Data", 9000, 16_500, 18),
        ("P02", "Trung tâm AI quốc gia", "AI", 8500, 15_600, 22),
        ("P03", "Định danh số mở rộng", "GovTech", 5200, 8_100, 10),
        ("P04", "Cloud chính phủ", "Infrastructure", 7600, 12_800, 14),
        ("P05", "Sandbox dữ liệu y tế", "Data", 4200, 7_600, 20),
        ("P06", "Chương trình đào tạo kỹ sư AI", "Human", 6800, 11_300, 8),
        ("P07", "Số hóa nông nghiệp ĐBSCL", "Inclusion", 5000, 9_000, 9),
        ("P08", "Bán dẫn và thiết kế chip", "AI", 11_500, 20_500, 24),
        ("P09", "An ninh mạng trọng yếu", "Cyber", 6200, 10_900, 12),
        ("P10", "Cổng dịch vụ công thế hệ mới", "GovTech", 4300, 6_900, 8),
        ("P11", "Quỹ đổi mới sáng tạo SME", "Inclusion", 7300, 12_600, 11),
        ("P12", "Logistics thông minh", "Infrastructure", 5700, 9_700, 13),
        ("P13", "AI tiếng Việt mã nguồn mở", "AI", 3900, 7_800, 16),
        ("P14", "Trường học số vùng khó", "Human", 4700, 8_900, 7),
        ("P15", "Hạ tầng dữ liệu xanh", "Infrastructure", 8100, 13_900, 15),
    ],
    columns=["project_id", "project_name", "category", "cost", "benefit", "risk"],
)

PRECEDENCE = [("P05", "P01"), ("P08", "P02"), ("P08", "P04"), ("P11", "P06"), ("P13", "P02")]
EXCLUSIONS = [("P03", "P10")]


def solve_project_mip(budget: float = 80_000.0, risk_cap: float = 145.0) -> dict:
    """Select projects with binary decisions under budget and logical constraints."""
    try:
        return _solve_project_mip_pulp(budget, risk_cap)
    except Exception:
        return _solve_project_mip_exhaustive(budget, risk_cap, solver_name="exhaustive_fallback")


def _solve_project_mip_pulp(budget: float = 80_000.0, risk_cap: float = 145.0) -> dict:
    import pulp

    projects = PROJECTS.copy()
    ids = projects["project_id"].tolist()
    by_id = projects.set_index("project_id")
    model = pulp.LpProblem("aideom_project_selection", pulp.LpMaximize)
    x = {pid: pulp.LpVariable(f"x_{pid}", lowBound=0, upBound=1, cat="Binary") for pid in ids}
    model += pulp.lpSum(float(by_id.loc[pid, "benefit"]) * x[pid] for pid in ids)
    model += pulp.lpSum(float(by_id.loc[pid, "cost"]) * x[pid] for pid in ids) <= budget, "budget"
    model += pulp.lpSum(float(by_id.loc[pid, "risk"]) * x[pid] for pid in ids) <= risk_cap, "risk_cap"

    for child, parent in PRECEDENCE:
        model += x[child] <= x[parent], f"precedence_{child}_{parent}"
    for a, b in EXCLUSIONS:
        model += x[a] + x[b] <= 1, f"exclusion_{a}_{b}"

    status = model.solve(pulp.PULP_CBC_CMD(msg=False))
    if pulp.LpStatus[status] != "Optimal":
        raise RuntimeError(f"PuLP/CBC status: {pulp.LpStatus[status]}")

    solution = np.array([int(round(pulp.value(x[pid]) or 0)) for pid in ids])
    feasible_count = np.nan
    return _format_solution(projects, solution, budget, risk_cap, feasible_count, "PuLP_CBC")


def _solve_project_mip_exhaustive(
    budget: float = 80_000.0,
    risk_cap: float = 145.0,
    solver_name: str = "exhaustive_binary_search",
) -> dict:
    """Fallback: enumerate all binary project portfolios."""
    projects = PROJECTS.copy()
    n = len(projects)
    best = None
    feasible_count = 0
    id_to_idx = {pid: i for i, pid in enumerate(projects["project_id"])}

    for bits in product([0, 1], repeat=n):
        x = np.array(bits)
        cost = float(np.dot(x, projects["cost"]))
        if cost > budget:
            continue
        risk = float(np.dot(x, projects["risk"]))
        if risk > risk_cap:
            continue
        ok = True
        for child, parent in PRECEDENCE:
            if x[id_to_idx[child]] > x[id_to_idx[parent]]:
                ok = False
                break
        if not ok:
            continue
        for a, b in EXCLUSIONS:
            if x[id_to_idx[a]] + x[id_to_idx[b]] > 1:
                ok = False
                break
        if not ok:
            continue
        feasible_count += 1
        benefit = float(np.dot(x, projects["benefit"]))
        if best is None or benefit > best["benefit"]:
            best = {"x": x, "cost": cost, "benefit": benefit, "risk": risk}

    if best is None:
        return {"success": False, "message": "Không tìm thấy phương án khả thi."}

    selected = projects[best["x"] == 1].copy()
    selected["selected"] = 1
    projects["selected"] = best["x"]
    return {
        "success": True,
        "selected": selected.reset_index(drop=True),
        "projects": projects,
        "total_cost": best["cost"],
        "total_benefit": best["benefit"],
        "total_risk": best["risk"],
        "feasible_count": feasible_count,
        "budget": budget,
        "risk_cap": risk_cap,
    }


def _format_solution(
    projects: pd.DataFrame,
    x: np.ndarray,
    budget: float,
    risk_cap: float,
    feasible_count: float,
    solver_name: str,
) -> dict:
    """Format a binary project solution in the same shape as the fallback."""
    cost = float(np.dot(x, projects["cost"]))
    benefit = float(np.dot(x, projects["benefit"]))
    risk = float(np.dot(x, projects["risk"]))
    selected = projects[x == 1].copy()
    selected["selected"] = 1
    projects["selected"] = x
    return {
        "success": True,
        "selected": selected.reset_index(drop=True),
        "projects": projects,
        "total_cost": cost,
        "total_benefit": benefit,
        "total_risk": risk,
        "feasible_count": feasible_count,
        "budget": budget,
        "risk_cap": risk_cap,
        "solver": solver_name,
    }
