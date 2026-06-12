"""AIDEOM-VN Streamlit decision dashboard for the final coursework."""

from __future__ import annotations

from datetime import datetime
import re
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from aideom_vn.data_loader import check_data_files, load_macro, load_regions, load_sectors
from aideom_vn.exercise01_cobb_douglas import (
    DEFAULT_PARAMS,
    forecast_2030,
    growth_contribution,
    run_cobb_douglas,
)
from aideom_vn.exercise02_lp_budget import (
    allocation_table,
    constraint_table,
    sensitivity_by_budget,
    solve_simple_budget_lp,
)
from aideom_vn.exercise03_priority import (
    DEFAULT_COLUMNS,
    DEFAULT_WEIGHTS,
    run_priority_model,
    sensitivity_top_sectors,
)
from aideom_vn.exercise04_region_sector_lp import solve_region_sector_lp
from aideom_vn.exercise05_project_mip import PROJECTS, solve_project_mip
from aideom_vn.exercise06_topsis import TOPSIS_CRITERIA, run_topsis
from aideom_vn.exercise07_pareto import run_pareto_search
from aideom_vn.exercise08_dynamic import optimize_dynamic_policy, simulate_dynamic_policy
from aideom_vn.exercise09_labor import find_training_threshold, simulate_labor_impact
from aideom_vn.exercise10_stochastic import solve_stochastic_policy
from aideom_vn.exercise11_qlearning import ACTION_SHARES, train_q_learning
from aideom_vn.exercise12_integrated import evaluate_scenarios, module_design_table
from aideom_vn.policy_briefs import (
    BriefSections,
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


st.set_page_config(
    page_title="AIDEOM-VN Decision Lab",
    page_icon="VN",
    layout="wide",
    initial_sidebar_state="expanded",
)


PAGES = [
    "Trang chủ",
    "Bài 1 - Cobb-Douglas + AI",
    "Bài 2 - LP ngân sách số",
    "Bài 3 - Priority 10 ngành",
    "Bài 4 - LP ngành-vùng",
    "Bài 5 - MIP 15 dự án",
    "Bài 6 - TOPSIS 6 vùng",
    "Bài 7 - NSGA-II Pareto",
    "Bài 8 - Động 2026-2035",
    "Bài 9 - Lao động & AI",
    "Bài 10 - Stochastic SP",
    "Bài 11 - Q-learning RL",
    "Bài 12 - AIDEOM tích hợp",
]

MODEL_VERSION = "2026-06-03-policy-brief-agent-v1"


def inject_style() -> None:
    st.markdown(
        """
        <style>
        .main .block-container { max-width: 1320px; padding-top: 1.6rem; }
        h1, h2, h3 { letter-spacing: 0; }
        .eyebrow { color: #0f766e; font-weight: 750; font-size: .82rem; text-transform: uppercase; }
        .brief {
            border-left: 4px solid #0f766e;
            background: #f8fafc;
            color: #172033;
            padding: 1rem 1.1rem;
            margin-top: .65rem;
            border-radius: 4px;
        }
        .brief-title {
            display: flex;
            align-items: center;
            gap: .55rem;
            color: #0f172a;
            font-size: 1.02rem;
            font-weight: 800;
            margin-bottom: .65rem;
        }
        .brief-chip {
            color: #0f766e;
            background: #dff8f3;
            border: 1px solid #9de4d9;
            border-radius: 4px;
            padding: .1rem .35rem;
            font-size: .72rem;
            font-weight: 760;
        }
        .brief b { color: #0f172a; }
        .brief li { margin-bottom: .35rem; }
        .note {
            background: #f8fafc;
            border: 1px solid #d9e2ef;
            color: #172033;
            padding: .9rem 1rem;
            border-radius: 6px;
        }
        div[data-testid="stMetricValue"] { color: #93c5fd; font-weight: 760; }
        div[data-testid="stMetricDelta"] { color: #4ade80; }
        div[data-testid="stDataFrame"] { border-radius: 6px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def get_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return load_macro(), load_sectors(), load_regions()


@st.cache_data
def cached_pareto(budget: float, population: int, generations: int, seed: int, model_version: str) -> dict:
    return run_pareto_search(budget=budget, population=population, generations=generations, seed=seed)


@st.cache_data
def cached_dynamic(_macro: pd.DataFrame, annual_budget: float, model_version: str) -> dict:
    return optimize_dynamic_policy(_macro, annual_budget=annual_budget)


@st.cache_data
def cached_stochastic(budget: float, model_version: str) -> dict:
    return solve_stochastic_policy(budget=budget)


@st.cache_data
def cached_qlearning(episodes: int, alpha: float, gamma: float, epsilon: float, seed: int, model_version: str) -> dict:
    return train_q_learning(episodes=episodes, alpha=alpha, gamma=gamma, epsilon=epsilon, seed=seed)


def fmt(value: float, digits: int = 1) -> str:
    text = f"{value:,.{digits}f}"
    return text.replace(",", "_").replace(".", ",").replace("_", ".")


def header(title: str, subtitle: str, tags: list[str]) -> None:
    st.markdown('<div class="eyebrow">AIDEOM-VN Decision Lab</div>', unsafe_allow_html=True)
    st.title(title)
    st.caption(subtitle)
    st.write(" ".join(f"`{tag}`" for tag in tags))


def render_policy_brief(sections: BriefSections) -> None:
    """Render the deterministic analysis agent output."""
    blocks = []
    for title, points in sections:
        items = "".join(f"<li>{point}</li>" for point in points)
        blocks.append(f"<b>{title}</b><ul>{items}</ul>")
    st.markdown(
        (
            "<div class='brief'>"
            "<div class='brief-title'>Tác nhân phân tích kết quả"
            "<span class='brief-chip'>theo tham số hiện tại</span></div>"
            f"{''.join(blocks)}</div>"
        ),
        unsafe_allow_html=True,
    )


def assumptions(points: list[str]) -> None:
    """Show compact modeling assumptions for the current model."""
    with st.expander("Giả định dữ liệu/tham số"):
        for point in points:
            st.write(f"- {point}")


def download_df(df: pd.DataFrame, name: str) -> None:
    st.download_button(
        "Tải bảng CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name=name,
        mime="text/csv",
        width="stretch",
    )


def _slug(text: str) -> str:
    """Create a filesystem-safe label for exported figures."""
    text = re.sub(r"[^0-9A-Za-z_-]+", "_", text.strip())
    return text.strip("_").lower() or "figure"


def show_chart(fig: go.Figure, figures: list[tuple[str, go.Figure]], label: str) -> None:
    """Render a Plotly figure and keep it for optional web export."""
    st.plotly_chart(fig, use_container_width=True)
    figures.append((label, fig))


def save_current_figures(page_id: str, figures: list[tuple[str, go.Figure]]) -> None:
    """Save current page figures as PNG and HTML, using current UI parameters."""
    if not figures:
        return
    st.divider()
    st.caption("Lưu figures của trang hiện tại theo đúng tham số đang chỉnh trên web.")
    if st.button("Lưu figures trang hiện tại", key=f"save_figures_{page_id}", width="stretch"):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = ROOT_DIR / "outputs" / "figures" / "web_exports" / page_id
        export_dir.mkdir(parents=True, exist_ok=True)
        saved: list[str] = []
        failed: list[str] = []
        for label, fig in figures:
            stem = f"{page_id}_{stamp}_{_slug(label)}"
            html_path = export_dir / f"{stem}.html"
            png_path = export_dir / f"{stem}.png"
            try:
                fig.write_html(html_path, include_plotlyjs="cdn")
                fig.write_image(png_path, scale=2)
                saved.extend([str(html_path), str(png_path)])
            except Exception as exc:  # pragma: no cover - UI fallback
                failed.append(f"{label}: {exc}")
        index_path = export_dir / "WEB_EXPORT_INDEX.md"
        with index_path.open("a", encoding="utf-8") as file:
            file.write(f"\n## {stamp}\n")
            for path in saved:
                file.write(f"- `{Path(path).name}`\n")
        if saved:
            st.success(f"Đã lưu {len(saved)} file vào {export_dir}")
            with st.expander("Danh sách file vừa lưu"):
                for path in saved:
                    st.code(path)
        if failed:
            st.warning("Một số biểu đồ chưa lưu được. Kiểm tra kaleido/Chrome nếu lỗi PNG.")
            for item in failed:
                st.write(item)


def home_page(macro: pd.DataFrame, sectors: pd.DataFrame, regions: pd.DataFrame) -> None:
    header(
        "AIDEOM-VN Policy Cockpit",
        "Không gian mô phỏng và tối ưu hóa quyết định phát triển kinh tế Việt Nam trong kỷ nguyên AI.",
        ["Dữ liệu 2020-2025", "Tối ưu hóa", "Dashboard chính sách"],
    )
    figures: list[tuple[str, go.Figure]] = []
    latest = macro.sort_values("year").iloc[-1]
    prev = macro.sort_values("year").iloc[-2]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("GDP 2025", f"{fmt(latest['GDP_billion_USD'])} tỷ USD", f"{latest['GDP_growth_pct']:.2f}%")
    c2.metric(
        "Kinh tế số/GDP",
        f"{latest['digital_economy_share_GDP_pct']:.1f}%",
        f"{latest['digital_economy_share_GDP_pct'] - prev['digital_economy_share_GDP_pct']:.1f} điểm",
    )
    c3.metric("FDI giải ngân", f"{latest['FDI_disbursed_billion_USD']:.1f} tỷ USD")
    c4.metric("GDP/người", f"{latest['GDP_per_capita_USD']:,.0f} USD".replace(",", "."))

    left, right = st.columns([1, 1], gap="large")
    with left:
        roadmap = pd.DataFrame(
            [
                ("Dễ", "Bài 1-3", "Cobb-Douglas, LP đơn giản, chỉ số ưu tiên"),
                ("Trung bình", "Bài 4-6", "LP ngành-vùng, MIP, TOPSIS"),
                ("Khá khó", "Bài 7-9", "Pareto, tối ưu động, lao động & AI"),
                ("Khó", "Bài 10-12", "Stochastic SP, Q-learning, dashboard tích hợp"),
            ],
            columns=["Cấp độ", "Phạm vi", "Trọng tâm"],
        )
        st.subheader("Bản đồ học phần")
        st.dataframe(roadmap, hide_index=True, width="stretch")
        st.subheader("Trạng thái dữ liệu")
        st.dataframe(check_data_files(), hide_index=True, width="stretch")
    with right:
        overview = macro[
            ["year", "GDP_trillion_VND", "exports_billion_USD", "FDI_disbursed_billion_USD"]
        ].copy()
        for column in ["GDP_trillion_VND", "exports_billion_USD", "FDI_disbursed_billion_USD"]:
            overview[column] = overview[column] / overview[column].iloc[0] * 100
        overview = overview.rename(
            columns={
                "GDP_trillion_VND": "GDP (chỉ số)",
                "exports_billion_USD": "Xuất khẩu (chỉ số)",
                "FDI_disbursed_billion_USD": "FDI giải ngân (chỉ số)",
            }
        )
        fig = px.line(
            overview,
            x="year",
            y=["GDP (chỉ số)", "Xuất khẩu (chỉ số)", "FDI giải ngân (chỉ số)"],
            markers=True,
            labels={"value": "Chỉ số (2020 = 100)", "year": "Năm", "variable": "Chỉ tiêu"},
        )
        fig.update_layout(
            title="Xu hướng vĩ mô chuẩn hóa theo năm 2020",
            height=410,
            margin=dict(l=10, r=10, t=40, b=10),
        )
        fig.update_yaxes(ticksuffix="")
        show_chart(fig, figures, "macro_overview")
        st.caption(
            "Ghi chú: GDP, xuất khẩu và FDI được chuẩn hóa theo năm gốc 2020 = 100 "
            "để so sánh tốc độ thay đổi tương đối giữa các chỉ tiêu khác đơn vị và quy mô."
        )
        render_policy_brief(home_brief(macro, sectors, regions))
    save_current_figures("home", figures)


def page01(macro: pd.DataFrame) -> None:
    header(
        "Bài 1 - Hàm sản xuất Cobb-Douglas mở rộng",
        "Ước lượng TFP, dự báo GDP, phân rã tăng trưởng và mô phỏng kịch bản 2030.",
        ["Cobb-Douglas", "Growth accounting", "MAPE"],
    )
    figures: list[tuple[str, go.Figure]] = []
    st.latex(r"Y_t=A_tK_t^\alpha L_t^\beta D_t^\gamma AI_t^\delta H_t^\theta")
    with st.expander("Điều chỉnh tham số Bài 1", expanded=True):
        st.caption("Thay đổi hệ số Cobb-Douglas và kịch bản 2030 để kiểm tra độ nhạy của kết quả.")
        c_alpha, c_beta, c_gamma, c_delta, c_theta = st.columns(5)
        alpha = c_alpha.slider("alpha - K", 0.20, 0.45, DEFAULT_PARAMS["alpha"], 0.01, key="bai01_alpha")
        beta = c_beta.slider("beta - L", 0.25, 0.55, DEFAULT_PARAMS["beta"], 0.01, key="bai01_beta")
        gamma = c_gamma.slider("gamma - D", 0.03, 0.20, DEFAULT_PARAMS["gamma"], 0.01, key="bai01_gamma")
        delta = c_delta.slider("delta - AI", 0.02, 0.18, DEFAULT_PARAMS["delta"], 0.01, key="bai01_delta")
        theta = 1 - alpha - beta - gamma - delta
        c_theta.metric("theta - H", f"{theta:.2f}")
        s_d, s_ai, s_h = st.columns(3)
        d2030 = s_d.slider("D 2030 (% GDP)", 20.0, 40.0, 30.0, 0.5, key="bai01_d2030")
        ai2030 = s_ai.slider("AI 2030 (nghìn DN)", 80.0, 140.0, 100.0, 1.0, key="bai01_ai2030")
        h2030 = s_h.slider("H 2030 (%)", 30.0, 45.0, 35.0, 0.5, key="bai01_h2030")
    if theta <= 0:
        st.error("Tổng hệ số đang vượt 1. Hãy giảm alpha, beta, gamma hoặc delta.")
        return
    params = {"alpha": alpha, "beta": beta, "gamma": gamma, "delta": delta, "theta": theta}
    result, metrics = run_cobb_douglas(macro, params)
    contribution = growth_contribution(result, params)
    forecast = forecast_2030(result, metrics, params, d2030, ai2030, h2030)
    c1, c2, c3 = st.columns(3)
    c1.metric("TFP trung bình", f"{metrics['a_bar']:.2f}")
    c2.metric("MAPE", f"{metrics['mape']:.2f}%")
    c3.metric("GDP 2030", f"{fmt(forecast['GDP_2030_trillion_VND'])} nghìn tỷ VND")
    t1, t2, t3, t4 = st.tabs(["TFP", "Dự báo", "Đóng góp tăng trưởng", "Kịch bản 2030"])
    with t1:
        table = result[["year", "Y", "K", "L", "D", "AI", "H", "TFP_A_t"]].round(4)
        st.dataframe(table, hide_index=True, width="stretch")
        fig = px.line(result, x="year", y="TFP_A_t", markers=True, color_discrete_sequence=["#0f766e"])
        show_chart(fig, figures, "tfp_trend")
    with t2:
        compare = result[["year", "Y", "Y_hat", "abs_pct_error"]].round(3)
        st.dataframe(compare, hide_index=True, width="stretch")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=result["year"], y=result["Y"], name="Thực tế", mode="lines+markers"))
        fig.add_trace(go.Scatter(x=result["year"], y=result["Y_hat"], name="Dự báo", mode="lines+markers"))
        show_chart(fig, figures, "actual_vs_predicted_gdp")
    with t3:
        st.dataframe(contribution.round(3), hide_index=True, width="stretch")
        fig = px.bar(contribution, x="factor", y="share_of_growth_pct", color="share_of_growth_pct")
        show_chart(fig, figures, "growth_contribution")
    with t4:
        st.dataframe(pd.DataFrame([forecast]).round(3), hide_index=True, width="stretch")
        assumptions(
            [
                "Kịch bản 2030 mặc định giả định vốn K tăng 6%/năm, lao động L tăng 0,6%/năm và TFP tăng 1,2%/năm.",
                "Mức tăng lao động dùng tốc độ dân số/lao động thận trọng; không giả định lực lượng lao động tăng 6%/năm.",
                "D, AI và H là tham số kịch bản để kiểm tra tác động chính sách, không phải dự báo chính thức.",
            ]
        )
        download_df(result, "bai01_cobb_douglas.csv")
    render_policy_brief(bai01_brief(result, metrics, forecast))
    save_current_figures("bai01", figures)


def page02() -> None:
    header("Bài 2 - LP phân bổ ngân sách số", "Tối ưu ngân sách 4 hạng mục và phân tích độ nhạy.", ["LP", "PuLP/CBC", "shadow price"])
    figures: list[tuple[str, go.Figure]] = []
    budget = st.slider("Tổng ngân sách (nghìn tỷ VND)", 80.0, 160.0, 100.0, 5.0)
    min_human = st.slider("Nhân lực số tối thiểu x3", 20.0, 40.0, 20.0, 1.0)
    result = solve_simple_budget_lp(budget, min_human)
    if not result["success"]:
        st.error(result["message"])
        return
    alloc = allocation_table(result)
    constraints = constraint_table(result)
    c1, c2 = st.columns(2)
    c1.metric("GDP gain tối ưu", f"{result['objective']:.2f}")
    c2.metric("Ngân sách sử dụng", f"{alloc['allocation'].sum():.1f}/{budget:.1f}")
    st.caption(f"Solver: {result.get('solver', 'LP solver')} | Shadow price: {result.get('shadow_price_source', 'n/a')}")
    t1, t2, t3 = st.tabs(["Phân bổ", "Ràng buộc", "Độ nhạy"])
    with t1:
        st.dataframe(alloc.round(3), hide_index=True, width="stretch")
        fig = px.bar(alloc, x="item", y="allocation", color="gdp_multiplier")
        show_chart(fig, figures, "budget_allocation")
    with t2:
        st.dataframe(constraints.round(4), hide_index=True, width="stretch")
    with t3:
        sens = sensitivity_by_budget([100, 120, 140, budget], min_human=min_human).drop_duplicates("budget")
        st.dataframe(sens.round(3), hide_index=True, width="stretch")
        fig = px.line(sens, x="budget", y="objective", markers=True)
        show_chart(fig, figures, "sensitivity_curve")
        download_df(sens, "bai02_sensitivity.csv")
    result["budget"] = budget
    render_policy_brief(bai02_brief(result, alloc, constraints))
    save_current_figures("bai02", figures)


def page03(sectors: pd.DataFrame) -> None:
    header("Bài 3 - Priority 10 ngành", "Chuẩn hóa min-max, gán trọng số và xếp hạng ngành ưu tiên.", ["MCDM", "Priority index", "Sensitivity"])
    figures: list[tuple[str, go.Figure]] = []
    labels = ["Tăng trưởng", "Việc làm", "Lan tỏa", "Xuất khẩu", "AI readiness", "Giảm rủi ro"]
    cols = st.columns(3)
    weights = []
    for i, label in enumerate(labels):
        with cols[i % 3]:
            weights.append(st.slider(label, 0.0, 0.5, DEFAULT_WEIGHTS[i], 0.01))
    ranked, normalized = run_priority_model(sectors, weights)
    t1, t2, t3 = st.tabs(["Xếp hạng", "Ma trận chuẩn hóa", "Độ nhạy"])
    with t1:
        st.dataframe(ranked[["sector_name_vi", "priority_score", "rank"] + DEFAULT_COLUMNS].round(3), hide_index=True, width="stretch")
        fig = px.bar(ranked, x="priority_score", y="sector_name_vi", orientation="h", color="ai_readiness_0_100")
        fig.update_layout(yaxis=dict(autorange="reversed"))
        show_chart(fig, figures, "priority_ranking")
    with t2:
        st.dataframe(normalized.round(3), hide_index=True, width="stretch")
    with t3:
        sens = sensitivity_top_sectors(sectors)
        st.dataframe(sens.round(3), hide_index=True, width="stretch")
        download_df(ranked, "bai03_priority.csv")
    render_policy_brief(bai03_brief(ranked, weights))
    save_current_figures("bai03", figures)


def page04(regions: pd.DataFrame, sectors: pd.DataFrame) -> None:
    header("Bài 4 - LP ngành-vùng", "Phân bổ ngân sách số theo vùng, ngành và hạng mục đầu tư.", ["LP", "Equity constraint", "Region-sector allocation"])
    figures: list[tuple[str, go.Figure]] = []
    budget = st.slider("Ngân sách (tỷ VND)", 30_000.0, 80_000.0, 50_000.0, 2_500.0)
    floor = st.slider("Sàn vùng yếu", 0.05, 0.15, 0.09, 0.01)
    cap = st.slider("Trần mỗi vùng", 0.25, 0.45, 0.32, 0.01)
    result = solve_region_sector_lp(regions, sectors, budget=budget, weak_region_floor=floor, max_region_share=cap)
    if not result["success"]:
        st.error(result["message"])
        return
    st.metric("GDP gain kỳ vọng", f"{fmt(result['objective'])}")
    t1, t2, t3 = st.tabs(["Top phân bổ", "Theo vùng/ngành/hạng mục", "Phân tích"])
    with t1:
        top = result["allocation"].head(25)
        st.dataframe(top.round(3), hide_index=True, width="stretch")
        fig = px.bar(top, x="allocation", y="sector_name_vi", color="region_name_vi", orientation="h")
        show_chart(fig, figures, "top_allocation")
    with t2:
        c1, c2, c3 = st.columns(3)
        c1.dataframe(result["region_summary"].round(2), hide_index=True, width="stretch")
        c2.dataframe(result["item_summary"].round(2), hide_index=True, width="stretch")
        c3.dataframe(result["sector_summary"].round(2), hide_index=True, width="stretch")
    with t3:
        assumptions(
            [
                "Hệ số vùng-ngành-hạng mục được xây dựng từ priority score ngành, AI readiness vùng, digital index và spillover.",
                "Ràng buộc sàn/trần theo vùng và trần theo ngành giúp nghiệm LP không dồn toàn bộ ngân sách vào một vùng/ngành.",
                "Kết quả là bản đồ ưu tiên phân bổ, chưa thay thế thẩm định dự án cụ thể.",
            ]
        )
        download_df(result["allocation"], "bai04_allocation.csv")
    render_policy_brief(bai04_brief(result))
    save_current_figures("bai04", figures)


def page05() -> None:
    header("Bài 5 - MIP lựa chọn dự án", "Chọn tập dự án chuyển đổi số dưới ngân sách, rủi ro và ràng buộc logic.", ["MIP", "PuLP/CBC", "Binary decision"])
    figures: list[tuple[str, go.Figure]] = []
    budget = st.slider("Ngân sách dự án (tỷ VND)", 50_000.0, 100_000.0, 80_000.0, 2_500.0)
    risk_cap = st.slider("Trần rủi ro", 80.0, 180.0, 145.0, 5.0)
    result = solve_project_mip(budget, risk_cap)
    if not result["success"]:
        st.error(result["message"])
        return
    c1, c2, c3 = st.columns(3)
    c1.metric("Lợi ích NPV", f"{fmt(result['total_benefit'])}")
    c2.metric("Chi phí", f"{fmt(result['total_cost'])}")
    c3.metric("Rủi ro", f"{result['total_risk']:.0f}/{risk_cap:.0f}")
    st.caption(f"Solver: {result.get('solver', 'PuLP_CBC hoặc fallback MIP')}")
    t1, t2 = st.tabs(["Dự án được chọn", "Toàn bộ danh mục"])
    with t1:
        st.dataframe(result["selected"], hide_index=True, width="stretch")
        assumptions(
            [
                "Danh mục 15 dự án là bộ danh mục chuẩn hóa để đánh giá lựa chọn đầu tư theo ngân sách, lợi ích và rủi ro.",
                "Cost, benefit và risk dùng cùng đơn vị tương đối trong mô hình; solver chính là PuLP/CBC.",
                "Ràng buộc precedence/exclusion thể hiện quan hệ phụ thuộc logic giữa các dự án chuyển đổi số.",
            ]
        )
    with t2:
        st.dataframe(result["projects"], hide_index=True, width="stretch")
        fig = px.bar(result["projects"], x="project_id", y="benefit", color="selected")
        show_chart(fig, figures, "project_benefit_selection")
        download_df(result["projects"], "bai05_projects.csv")
    render_policy_brief(bai05_brief(result, len(PROJECTS), budget, risk_cap))
    save_current_figures("bai05", figures)


def page06(regions: pd.DataFrame) -> None:
    header("Bài 6 - TOPSIS 6 vùng", "Xếp hạng vùng ưu tiên đầu tư AI bằng entropy weight và TOPSIS.", ["TOPSIS", "Entropy weight", "Regional ranking"])
    figures: list[tuple[str, go.Figure]] = []
    ranking, weights = run_topsis(regions)
    c1, c2 = st.columns([1.1, 0.9])
    with c1:
        st.dataframe(ranking.round(4), hide_index=True, width="stretch")
        fig = px.bar(ranking, x="TOPSIS_score", y="region_name_vi", orientation="h", color="TOPSIS_score")
        show_chart(fig, figures, "topsis_ranking")
    with c2:
        weight_df = weights.reset_index()
        weight_df.columns = ["criterion", "weight"]
        st.dataframe(weight_df.round(4), hide_index=True, width="stretch")
        fig = px.bar(weight_df, x="weight", y="criterion", orientation="h")
        show_chart(fig, figures, "entropy_weights")
    render_policy_brief(bai06_brief(ranking, weights))
    save_current_figures("bai06", figures)


def page07() -> None:
    header("Bài 7 - Tối ưu đa mục tiêu Pareto", "Tìm tập nghiệm đánh đổi giữa tăng trưởng, bao trùm, xanh hóa và an ninh dữ liệu.", ["Pareto", "pymoo NSGA-II", "Compromise"])
    figures: list[tuple[str, go.Figure]] = []
    budget = st.slider("Ngân sách Pareto (tỷ VND)", 50_000.0, 120_000.0, 80_000.0, 5_000.0)
    population = st.slider("Population", 30, 150, 80, 10)
    generations = st.slider("Số thế hệ", 30, 150, 80, 10)
    seed = st.number_input("Seed", value=42, step=1)
    result = cached_pareto(budget, population, generations, int(seed), MODEL_VERSION)
    pareto = result["pareto"]
    comp = result["compromise"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Số nghiệm Pareto", len(pareto))
    c2.metric("GDP gain thỏa hiệp", f"{fmt(comp['gdp_gain'])}")
    c3.metric("Risk index", f"{comp['risk_index']:.3f}")
    st.caption(f"Solver: {result.get('solver', comp.get('solver', 'NSGA-II'))}")
    t1, t2 = st.tabs(["Pareto frontier", "Nghiệm thỏa hiệp"])
    with t1:
        fig = px.scatter(pareto, x="gdp_gain", y="inclusion", color="risk_index", size="green_score", hover_data=["K_share", "D_share", "AI_share", "H_share"])
        show_chart(fig, figures, "pareto_frontier")
        st.dataframe(pareto.head(40).round(4), hide_index=True, width="stretch")
    with t2:
        shares = pd.DataFrame({"item": ["K", "D", "AI", "H"], "share": [comp["K_share"], comp["D_share"], comp["AI_share"], comp["H_share"]]})
        st.dataframe(shares.round(4), hide_index=True, width="stretch")
        fig = px.pie(shares, names="item", values="share", hole=0.45)
        show_chart(fig, figures, "compromise_shares")
        assumptions(
            [
                "Hàm mục tiêu Pareto gồm GDP gain, inclusion, green score và data security để lượng hóa đánh đổi chính sách.",
                "Mỗi tỷ trọng K/D/AI/H bị chặn trong khoảng 10%-70% để tránh nghiệm cực đoan khó triển khai.",
                "Nghiệm thỏa hiệp được chọn bằng điểm chuẩn hóa, có phạt rủi ro và phạt cơ cấu quá lệch khỏi cân bằng.",
            ]
        )
    render_policy_brief(bai07_brief(result))
    save_current_figures("bai07", figures)


def page08(macro: pd.DataFrame) -> None:
    header("Bài 8 - Tối ưu động 2026-2035", "Tìm cơ cấu đầu tư liên thời gian tối ưu theo GDP chiết khấu.", ["Dynamic optimization", "CVXPY/SLSQP", "State path"])
    figures: list[tuple[str, go.Figure]] = []
    annual_budget = st.slider("Ngân sách hằng năm (nghìn tỷ VND)", 300.0, 1_000.0, 650.0, 50.0)
    result = cached_dynamic(macro, annual_budget, MODEL_VERSION)
    best = result["best"]
    trajectory = result["trajectory"]
    baseline = simulate_dynamic_policy(macro, {"K": 0.30, "D": 0.25, "AI": 0.25, "H": 0.20}, annual_budget)
    c1, c2 = st.columns(2)
    c1.metric("GDP 2035 tối ưu", f"{fmt(best['GDP_2035'])} nghìn tỷ")
    c2.metric("Điểm mục tiêu", f"{fmt(best['score'])}")
    st.caption(f"Solver: {result.get('solver', best.get('solver', 'dynamic optimizer'))}")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trajectory["year"], y=trajectory["GDP"], name="Tối ưu", mode="lines+markers"))
    fig.add_trace(go.Scatter(x=baseline["year"], y=baseline["GDP"], name="Cân bằng cố định", mode="lines+markers"))
    show_chart(fig, figures, "gdp_path_2026_2035")
    shares = pd.DataFrame({"item": ["K", "D", "AI", "H"], "share": [best["K"], best["D"], best["AI"], best["H"]]})
    st.dataframe(shares.round(3), hide_index=True, width="stretch")
    assumptions(
        [
            "Bài 8 dùng mô hình tối ưu liên thời gian với biến trạng thái K, D, AI, H và tỷ trọng quyết định theo từng năm.",
            "Solver ưu tiên CVXPY nếu môi trường có cài đặt; nếu không, dùng SLSQP cho bài toán nonlinear path optimization trước khi rơi về grid fallback.",
            "Đường cơ sở dùng cơ cấu cố định để so sánh lợi ích của tối ưu hóa liên thời gian.",
        ]
    )
    render_policy_brief(bai08_brief(result, baseline))
    save_current_figures("bai08", figures)


def page09(sectors: pd.DataFrame) -> None:
    header("Bài 9 - Tác động AI tới lao động", "Mô phỏng JobLoss, JobCreation và NetJob theo ngành.", ["Labor simulation", "NetJob", "Reskilling"])
    figures: list[tuple[str, go.Figure]] = []
    adoption = st.slider("Tỷ lệ ứng dụng AI", 0.20, 0.75, 0.45, 0.05)
    training = st.slider("Ngân sách đào tạo lại (tỷ VND)", 0.0, 250_000.0, 30_000.0, 5_000.0)
    ai_inv = st.slider("Đầu tư AI (tỷ VND)", 10_000.0, 120_000.0, 40_000.0, 5_000.0)
    result = simulate_labor_impact(sectors, adoption, training, ai_inv)
    threshold = find_training_threshold(sectors, adoption, ai_inv)
    c1, c2 = st.columns(2)
    c1.metric("NetJob toàn nền kinh tế", f"{result['net_job_million'].sum():.3f} triệu")
    c2.metric("Ngưỡng đào tạo tối thiểu", "Không tìm thấy" if pd.isna(threshold["threshold"]) else f"{fmt(threshold['threshold'], 0)} tỷ VND")
    st.dataframe(result[["sector_name_vi", "job_loss_million", "new_jobs_million", "jobs_saved_million", "net_job_million"]].round(4), hide_index=True, width="stretch")
    fig = px.bar(result, x="net_job_million", y="sector_name_vi", orientation="h", color="net_job_million")
    show_chart(fig, figures, "netjob_by_sector")
    render_policy_brief(bai09_brief(result, threshold))
    save_current_figures("bai09", figures)


def page10() -> None:
    header("Bài 10 - Quy hoạch ngẫu nhiên hai giai đoạn", "Ra quyết định ngân sách khi cầu xuất khẩu, FDI và rủi ro bất định.", ["Two-stage SP", "Pyomo", "VSS/EVPI"])
    figures: list[tuple[str, go.Figure]] = []
    budget = st.slider("Ngân sách stochastic (tỷ VND)", 50_000.0, 120_000.0, 80_000.0, 5_000.0)
    result = cached_stochastic(budget, MODEL_VERSION)
    policy = result["stochastic_policy"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Expected value", f"{fmt(policy['expected_value'])}")
    c2.metric("VSS", f"{fmt(result['vss'])}")
    c3.metric("EVPI", f"{fmt(result['evpi'])}")
    st.caption(f"Solver: {result.get('solver', policy.get('solver', 'Pyomo hoặc fallback stochastic'))}")
    values = result["scenario_values"]
    st.dataframe(values.round(3), hide_index=True, width="stretch")
    fig = px.bar(values, x="scenario", y="value", color="recourse_cost")
    show_chart(fig, figures, "scenario_values")
    shares = pd.DataFrame({"item": ["K", "D", "AI", "H"], "share": [policy["K"], policy["D"], policy["AI"], policy["H"]]})
    st.dataframe(shares.round(3), hide_index=True, width="stretch")
    assumptions(
        [
            "Ba kịch bản lạc quan/cơ sở/bi quan đại diện cho các trạng thái cầu, FDI và rủi ro khác nhau.",
            "Tỷ trọng AI bị giới hạn tối đa 50% và nhân lực số tối thiểu 15% để phản ánh năng lực hấp thụ chính sách.",
            "Solver chính là Pyomo với appsi_highs; các dòng comparison_grid chỉ để so sánh ứng viên chính sách.",
            "Recourse cost biểu diễn chi phí điều chỉnh khi cầu thấp hơn kịch bản cơ sở.",
        ]
    )
    render_policy_brief(bai10_brief(result))
    save_current_figures("bai10", figures)


def page11() -> None:
    header("Bài 11 - Q-learning chính sách thích nghi", "Huấn luyện Q-table để chọn hành động phân bổ theo trạng thái kinh tế.", ["Q-learning", "MDP", "Adaptive policy"])
    figures: list[tuple[str, go.Figure]] = []
    episodes = st.slider("Episodes", 100, 2_000, 700, 100)
    alpha = st.slider("Learning rate", 0.05, 0.50, 0.18, 0.01)
    gamma = st.slider("Discount factor", 0.50, 0.99, 0.90, 0.01)
    epsilon = st.slider("Epsilon", 0.02, 0.40, 0.18, 0.01)
    result = cached_qlearning(episodes, alpha, gamma, epsilon, 42, MODEL_VERSION)
    t1, t2, t3 = st.tabs(["Chính sách học được", "Q-table", "Reward"])
    with t1:
        st.dataframe(result["policy"], hide_index=True, width="stretch")
        st.dataframe(pd.DataFrame(ACTION_SHARES).T.reset_index().rename(columns={"index": "action"}), hide_index=True, width="stretch")
        assumptions(
            [
                "Trạng thái MDP và reward được thiết kế để lượng hóa chính sách thích nghi theo trạng thái kinh tế.",
                "Các hành động là 5 cấu hình phân bổ K/D/AI/H rời rạc, phù hợp bài Q-learning tabular.",
                "Kết quả phản ánh logic học tăng cường trong môi trường trạng thái-hành động rời rạc.",
            ]
        )
    with t2:
        st.dataframe(result["q_table"].round(3), width="stretch")
        fig = px.imshow(result["q_table"], text_auto=".1f", aspect="auto", color_continuous_scale="Teal")
        show_chart(fig, figures, "q_table_heatmap")
    with t3:
        trace = result["reward_trace"].copy()
        trace["rolling_reward"] = trace["reward"].rolling(30, min_periods=1).mean()
        fig = px.line(trace, x="episode", y=["reward", "rolling_reward"])
        show_chart(fig, figures, "reward_trace")
    render_policy_brief(bai11_brief(result))
    save_current_figures("bai11", figures)


def page12(sectors: pd.DataFrame) -> None:
    header("Bài 12 - AIDEOM-VN tích hợp", "Dashboard tổng hợp 6 module và 6 kịch bản chính sách.", ["Integrated dashboard", "Scenario comparison", "AIDEOM-VN"])
    figures: list[tuple[str, go.Figure]] = []
    budget = st.slider("Tổng ngân sách kịch bản (tỷ VND)", 50_000.0, 120_000.0, 80_000.0, 5_000.0)
    scenarios = evaluate_scenarios(sectors, budget)
    c1, c2, c3 = st.columns(3)
    c1.metric("Kịch bản tốt nhất", scenarios.iloc[0]["scenario"])
    c2.metric("Overall score", f"{scenarios.iloc[0]['overall_score']:.3f}")
    c3.metric("NetJob cao nhất", f"{scenarios['net_job_million'].max():.3f} triệu")
    t1, t2, t3 = st.tabs(["So sánh kịch bản", "Radar KPI", "Thiết kế hệ thống"])
    with t1:
        st.dataframe(scenarios.round(4), hide_index=True, width="stretch")
        fig = px.bar(scenarios, x="scenario", y=["GDP_gain", "inclusion"], barmode="group")
        show_chart(fig, figures, "scenario_comparison")
    with t2:
        best = scenarios.iloc[0]
        categories = ["GDP_gain", "inclusion", "net_job_million", "overall_score"]
        values = []
        for cat in categories:
            col = scenarios[cat]
            values.append((best[cat] - col.min()) / (col.max() - col.min() + 1e-12))
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill="toself", name=best["scenario"]))
        fig.update_layout(height=450, polar=dict(radialaxis=dict(visible=True, range=[0, 1])))
        show_chart(fig, figures, "best_scenario_radar")
    with t3:
        st.dataframe(module_design_table(), hide_index=True, width="stretch")
        download_df(scenarios, "bai12_scenarios.csv")
    render_policy_brief(bai12_brief(scenarios))
    save_current_figures("bai12", figures)


def main() -> None:
    inject_style()
    macro, sectors, regions = get_data()
    with st.sidebar:
        st.title("AIDEOM-VN")
        st.caption("Web app mô hình ra quyết định phát triển kinh tế Việt Nam")
        page = st.radio("Menu", PAGES, label_visibility="collapsed")
        st.divider()
        st.caption(f"Project: `{ROOT_DIR}`")
        st.caption("Nguồn: NSO/GSO, MoST, MIC, MPI, WB, WIPO")

    if page == "Trang chủ":
        home_page(macro, sectors, regions)
    elif page == "Bài 1 - Cobb-Douglas + AI":
        page01(macro)
    elif page == "Bài 2 - LP ngân sách số":
        page02()
    elif page == "Bài 3 - Priority 10 ngành":
        page03(sectors)
    elif page == "Bài 4 - LP ngành-vùng":
        page04(regions, sectors)
    elif page == "Bài 5 - MIP 15 dự án":
        page05()
    elif page == "Bài 6 - TOPSIS 6 vùng":
        page06(regions)
    elif page == "Bài 7 - NSGA-II Pareto":
        page07()
    elif page == "Bài 8 - Động 2026-2035":
        page08(macro)
    elif page == "Bài 9 - Lao động & AI":
        page09(sectors)
    elif page == "Bài 10 - Stochastic SP":
        page10()
    elif page == "Bài 11 - Q-learning RL":
        page11()
    elif page == "Bài 12 - AIDEOM tích hợp":
        page12(sectors)


if __name__ == "__main__":
    main()

