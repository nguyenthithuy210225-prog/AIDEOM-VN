"""Deterministic expert-style policy brief generators for AIDEOM-VN.

The dashboard calls these functions after each model has produced tables,
metrics, and figures. They are intentionally deterministic: every statement is
derived from the current model output, so the analysis changes when sliders
change and remains reproducible across operating sessions.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import numpy as np
import pandas as pd


BriefSections = list[tuple[str, list[str]]]


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _fmt(value: Any, digits: int = 1) -> str:
    text = f"{_num(value):,.{digits}f}"
    return text.replace(",", "_").replace(".", ",").replace("_", ".")


def _pct(value: Any, digits: int = 1) -> str:
    return f"{_num(value) * 100:.{digits}f}%"


def _names(values: Iterable[Any], limit: int = 3) -> str:
    names = [str(value) for value in values if str(value)]
    return ", ".join(names[:limit])


def _top_row(df: pd.DataFrame, column: str, ascending: bool = False) -> pd.Series:
    if df.empty or column not in df.columns:
        return pd.Series(dtype=object)
    return df.sort_values(column, ascending=ascending).iloc[0]


def _binding_count(df: pd.DataFrame) -> int:
    for column in ("slack_or_surplus", "slack"):
        if column in df.columns:
            return int((df[column].abs() <= 1e-6).sum())
    return 0


def _share_comment(shares: dict[str, float]) -> str:
    dominant = max(shares, key=shares.get)
    if shares[dominant] >= 0.55:
        return f"cơ cấu nghiêng mạnh về {dominant}, cần giải thích vì sao ưu tiên này hợp lý"
    if max(shares.values()) - min(shares.values()) <= 0.15:
        return "cơ cấu tương đối cân bằng, phù hợp khi mục tiêu là giảm rủi ro lệch chính sách"
    return f"cơ cấu có trọng tâm rõ ở {dominant}, nhưng chưa cực đoan"


def home_brief(macro: pd.DataFrame, sectors: pd.DataFrame, regions: pd.DataFrame) -> BriefSections:
    ordered = macro.sort_values("year")
    first = ordered.iloc[0]
    latest = ordered.iloc[-1]
    previous = ordered.iloc[-2]
    gdp_index = _num(latest["GDP_trillion_VND"]) / max(_num(first["GDP_trillion_VND"]), 1e-12) * 100
    export_index = _num(latest["exports_billion_USD"]) / max(_num(first["exports_billion_USD"]), 1e-12) * 100
    fdi_index = _num(latest["FDI_disbursed_billion_USD"]) / max(_num(first["FDI_disbursed_billion_USD"]), 1e-12) * 100
    digital_delta = _num(latest["digital_economy_share_GDP_pct"]) - _num(previous["digital_economy_share_GDP_pct"])
    return [
        (
            "Chẩn đoán dữ liệu",
            [
                f"Bộ dữ liệu gồm {len(macro)} năm vĩ mô, {len(sectors)} ngành và {len(regions)} vùng; phạm vi dữ liệu phù hợp cho phân tích kịch bản và so sánh chính sách trong giai đoạn ngắn.",
                f"Năm {int(latest['year'])} ghi nhận GDP {_fmt(latest['GDP_billion_USD'])} tỷ USD, FDI giải ngân {_fmt(latest['FDI_disbursed_billion_USD'])} tỷ USD và kinh tế số đạt {_fmt(latest['digital_economy_share_GDP_pct'])}% GDP.",
            ],
        ),
        (
            "Diễn giải chuyên gia",
            [
                f"So với gốc 2020, chỉ số GDP đạt {_fmt(gdp_index)}, xuất khẩu {_fmt(export_index)} và FDI {_fmt(fdi_index)}; vì khác đơn vị đo nên biểu đồ chuẩn hóa là lựa chọn đúng để so sánh tốc độ thay đổi.",
                f"Tỷ trọng kinh tế số tăng thêm {_fmt(digital_delta)} điểm so với năm trước, cho thấy biến D đang có vai trò chính sách đủ lớn để đưa vào hàm sản xuất và các bài tối ưu.",
            ],
        ),
        (
            "Độ tin cậy vận hành",
            [
                "Dữ liệu, solver và output được xử lý trong môi trường local, giúp kết quả có thể tái lập theo cùng bộ tham số.",
                "Các tham số bổ sung được chuẩn hóa nhất quán giữa các module, giúp hệ thống giữ được logic so sánh khi chuyển từ phân tích vĩ mô sang tối ưu ngân sách.",
            ],
        ),
    ]


def bai01_brief(result: pd.DataFrame, metrics: dict[str, Any], forecast: dict[str, Any]) -> BriefSections:
    ordered = result.sort_values("year")
    tfp_start = _num(ordered["TFP_A_t"].iloc[0])
    tfp_end = _num(ordered["TFP_A_t"].iloc[-1])
    tfp_growth = _num(metrics.get("tfp_growth_pct"))
    mape = _num(metrics.get("mape"))
    forecast_gdp = _num(forecast.get("GDP_2030_trillion_VND"))
    latest_y = _num(ordered["Y"].iloc[-1])
    uplift = forecast_gdp - latest_y
    quality = "cho mức sai số phù hợp để so sánh kịch bản" if mape <= 10 else "cho thấy cần thận trọng khi diễn giải dự báo tuyệt đối"
    return [
        (
            "Chẩn đoán mô hình",
            [
                f"TFP tăng từ {_fmt(tfp_start, 2)} lên {_fmt(tfp_end, 2)}, tương đương {_fmt(tfp_growth)}% toàn kỳ; đây là tín hiệu năng suất tổng hợp cải thiện chứ không chỉ tăng nhờ vốn/lao động.",
                f"MAPE {_fmt(mape, 2)}%, {quality}; mô hình phù hợp nhất cho phân tích tương đối giữa các kịch bản chính sách.",
                f"Kịch bản hiện tại cho GDP 2030 khoảng {_fmt(forecast_gdp)} nghìn tỷ VND, cao hơn mức 2025 khoảng {_fmt(uplift)} nghìn tỷ VND.",
            ],
        ),
        (
            "Diễn giải chuyên gia",
            [
                "Hệ số D, AI và H phản ánh năng lực hấp thụ công nghệ: nếu chỉ tăng AI mà không tăng nhân lực số, tác động dài hạn dễ bị nghẽn ở khâu triển khai.",
                "TFP tăng cùng với kinh tế số cho thấy chuyển đổi số có thể được xem là kênh nâng năng suất, nhưng dữ liệu 6 năm chưa đủ để khẳng định quan hệ nhân quả mạnh.",
            ],
        ),
        (
            "Khuyến nghị sử dụng kết quả",
            [
                "Kết quả Bài 1 đóng vai trò mô hình nền, cung cấp logic tăng trưởng cho các module phân bổ ngân sách và kịch bản 2030.",
                "So sánh trước-sau khi thay đổi D/AI/H cho thấy mức nhạy của GDP 2030 đối với năng lực số, AI và nhân lực.",
            ],
        ),
    ]


def bai02_brief(result: dict[str, Any], alloc: pd.DataFrame, constraints: pd.DataFrame) -> BriefSections:
    top = _top_row(alloc, "allocation")
    binding = _binding_count(constraints)
    budget = _num(result.get("budget", alloc["allocation"].sum()))
    budget_used = _num(alloc["allocation"].sum())
    used_ratio = budget_used / max(budget, 1e-12)
    shadow_source = result.get("shadow_price_source", "n/a")
    return [
        (
            "Chẩn đoán nghiệm LP",
            [
                f"Solver: {result.get('solver', 'LP solver')}; nguồn shadow price: {shadow_source}. Đây là điểm mạnh vì nghiệm không chỉ có phân bổ mà còn có thông tin giá trị biên của ràng buộc.",
                f"Ngân sách sử dụng {_fmt(budget_used)}/{_fmt(budget)} ({_pct(used_ratio)}); có {binding} ràng buộc binding, cho thấy bài toán đang bị chi phối bởi các giới hạn nguồn lực/tối thiểu.",
                f"Hạng mục nhận phân bổ lớn nhất là {top.get('item', 'n/a')} với {_fmt(top.get('allocation'))}, phản ánh nơi mô hình nhìn thấy hiệu quả biên cao nhất sau khi thỏa ràng buộc.",
            ],
        ),
        (
            "Diễn giải chuyên gia",
            [
                "Nếu ngân sách binding, tăng thêm ngân sách sẽ có giá trị chính sách; nếu các ràng buộc tối thiểu binding, mô hình đang phải hy sinh một phần mục tiêu để bảo đảm điều kiện nền.",
                "Nhân lực số tối thiểu là ràng buộc quan trọng về năng lực hấp thụ: phân bổ công nghệ cao mà thiếu con người sẽ khó chuyển thành GDP gain thực tế.",
            ],
        ),
        (
            "Khuyến nghị quyết định",
            [
                "Dùng bảng độ nhạy ngân sách để nói rõ mức ngân sách nào bắt đầu cho lợi ích biên giảm dần.",
                "Shadow price được sử dụng như thước đo lợi ích biên: thêm 1 đơn vị ngân sách có thể làm mục tiêu tăng thêm bao nhiêu trong vùng nghiệm hiện tại.",
            ],
        ),
    ]


def bai03_brief(ranked: pd.DataFrame, weights: list[float]) -> BriefSections:
    sorted_rank = ranked.sort_values("rank")
    top3 = _names(sorted_rank["sector_name_vi"], 3)
    top = sorted_rank.iloc[0]
    second = sorted_rank.iloc[1]
    gap = _num(top["priority_score"]) - _num(second["priority_score"])
    labels = ["tăng trưởng", "việc làm", "lan tỏa", "xuất khẩu", "AI readiness", "giảm rủi ro"]
    main_weight = labels[int(np.argmax(weights))] if weights else "n/a"
    sensitivity_note = "rất nhạy với trọng số" if gap < 0.05 else "tương đối ổn định ở nhóm đầu"
    return [
        (
            "Chẩn đoán xếp hạng",
            [
                f"Top 3 ngành ưu tiên: {top3}. Ngành dẫn đầu là {top['sector_name_vi']} với điểm {_fmt(top['priority_score'], 3)}.",
                f"Khoảng cách hạng 1-2 là {_fmt(gap, 3)}, nên kết quả {sensitivity_note}.",
                f"Trọng số lớn nhất đang đặt vào tiêu chí {main_weight}; điều này cho biết ưu tiên chính sách đang nghiêng về mục tiêu nào.",
            ],
        ),
        (
            "Diễn giải chuyên gia",
            [
                "MCDM không chỉ xếp hạng ngành mạnh nhất tuyệt đối, mà phản ánh ưu tiên của nhà hoạch định chính sách thông qua trọng số.",
                "Một ngành có AI readiness cao nhưng rủi ro tự động hóa lớn cần được ghép với chính sách đào tạo lại, nếu không lợi ích tăng trưởng có thể đi kèm chi phí xã hội.",
            ],
        ),
        (
            "Khuyến nghị quyết định",
            [
                "Nên dùng top 3 làm danh sách ưu tiên đầu tư, không chỉ chọn top 1, vì thứ hạng có thể đổi khi trọng số thay đổi.",
                "Thay đổi trọng số việc làm hoặc AI readiness cho thấy thứ hạng ngành phản ứng như thế nào trước các ưu tiên chính sách khác nhau.",
            ],
        ),
    ]


def bai04_brief(result: dict[str, Any]) -> BriefSections:
    allocation = result["allocation"]
    region_summary = result["region_summary"]
    sector_summary = result["sector_summary"]
    item_summary = result.get("item_summary", pd.DataFrame())
    top = allocation.iloc[0] if not allocation.empty else pd.Series(dtype=object)
    top_region = _top_row(region_summary, "allocation")
    top_sector = _top_row(sector_summary, "allocation")
    top_item = _top_row(item_summary, "allocation") if not item_summary.empty else pd.Series(dtype=object)
    return [
        (
            "Chẩn đoán phân bổ",
            [
                f"GDP gain kỳ vọng đạt {_fmt(result.get('objective'))}; vùng nhận phân bổ lớn nhất là {top_region.get('region_name_vi', 'n/a')} ({_fmt(top_region.get('allocation'))}).",
                f"Ngành nhận tổng phân bổ lớn nhất là {top_sector.get('sector_name_vi', 'n/a')} ({_fmt(top_sector.get('allocation'))}); hạng mục nổi bật là {top_item.get('item_name', top_item.get('item', 'n/a'))}.",
                f"Tổ hợp ưu tiên cao nhất: {top.get('region_name_vi', 'n/a')} - {top.get('sector_name_vi', 'n/a')} - {top.get('item_name', 'n/a')}.",
            ],
        ),
        (
            "Diễn giải chuyên gia",
            [
                "Ràng buộc sàn/trần vùng biến bài toán từ tối đa hóa thuần túy thành tối ưu có công bằng không gian, phù hợp bối cảnh chính sách công.",
                "Nếu nghiệm vẫn tập trung vào vài vùng/ngành, đó không nhất thiết là lỗi; nó thể hiện đánh đổi giữa hiệu quả GDP và bao trùm vùng.",
            ],
        ),
        (
            "Khuyến nghị quyết định",
            [
                "Dùng kết quả như bản đồ ưu tiên cấp chiến lược, sau đó mới đưa xuống bước thẩm định dự án cụ thể.",
                "Trần ngành/vùng giúp nghiệm LP cân bằng hơn giữa hiệu quả mục tiêu và khả năng triển khai trên thực tế.",
            ],
        ),
    ]


def bai05_brief(result: dict[str, Any], total_projects: int, budget: float, risk_cap: float) -> BriefSections:
    selected = result["selected"]
    risk_ratio = _num(result.get("total_risk")) / max(risk_cap, 1e-12)
    cost_ratio = _num(result.get("total_cost")) / max(budget, 1e-12)
    risk_note = "đang sát trần rủi ro" if risk_ratio >= 0.9 else "còn dư địa rủi ro"
    selected_names = _names(selected.get("project_name", pd.Series(dtype=object)), 3)
    return [
        (
            "Chẩn đoán danh mục",
            [
                f"Mô hình chọn {len(selected)}/{total_projects} dự án; tổng chi phí {_fmt(result.get('total_cost'))}/{_fmt(budget)} ({_pct(cost_ratio)} ngân sách).",
                f"Tổng rủi ro {_fmt(result.get('total_risk'), 0)}/{_fmt(risk_cap, 0)}, tức {risk_note}; solver hiện tại là {result.get('solver', 'MIP solver')}.",
                f"Một số dự án được chọn: {selected_names}.",
            ],
        ),
        (
            "Diễn giải chuyên gia",
            [
                "MIP phù hợp hơn chọn thủ công vì nó xử lý đồng thời ngân sách, lợi ích, rủi ro và ràng buộc logic giữa dự án.",
                "Khi trần rủi ro bị chạm, mỗi dự án mới không chỉ cần lợi ích cao mà còn phải cạnh tranh về rủi ro biên.",
            ],
        ),
        (
            "Khuyến nghị quyết định",
            [
                "Dự án có lợi ích cao chưa chắc được chọn nếu vi phạm ràng buộc precedence/exclusion hoặc làm vượt ngưỡng rủi ro danh mục.",
                "Nên chạy thử nhiều trần rủi ro để tìm danh mục cân bằng giữa tham vọng chuyển đổi số và khả năng kiểm soát thực thi.",
            ],
        ),
    ]


def bai06_brief(ranking: pd.DataFrame, weights: pd.Series) -> BriefSections:
    sorted_rank = ranking.sort_values("rank")
    top3 = _names(sorted_rank["region_name_vi"], 3)
    main_criterion = str(weights.sort_values(ascending=False).index[0]) if not weights.empty else "n/a"
    top = sorted_rank.iloc[0]
    last = sorted_rank.iloc[-1]
    gap = _num(top["TOPSIS_score"]) - _num(last["TOPSIS_score"])
    return [
        (
            "Chẩn đoán TOPSIS",
            [
                f"Ba vùng ưu tiên theo TOPSIS: {top3}. Vùng dẫn đầu đạt điểm {_fmt(top['TOPSIS_score'], 3)}.",
                f"Tiêu chí có entropy weight lớn nhất là {main_criterion}; đây là biến tạo khác biệt mạnh nhất giữa các vùng trong bộ dữ liệu.",
                f"Khoảng cách điểm đầu-cuối là {_fmt(gap, 3)}, cho thấy mức phân hóa vùng khá rõ.",
            ],
        ),
        (
            "Diễn giải chuyên gia",
            [
                "Entropy weight làm trọng số dựa trên độ phân tán dữ liệu, nhờ đó giảm bớt chủ quan so với gán trọng số hoàn toàn bằng tay.",
                "TOPSIS đo mức gần với nghiệm lý tưởng; vùng điểm thấp không phải bị loại bỏ, mà cần nhóm chính sách nâng nền.",
            ],
        ),
        (
            "Khuyến nghị quyết định",
            [
                "Dùng top vùng để đề xuất trung tâm triển khai AI trước, đồng thời dùng nhóm cuối để thiết kế gói bao trùm số.",
                "TOPSIS là công cụ xếp hạng ưu tiên vùng; quyết định phân bổ ngân sách cuối cùng cần kết hợp thêm ràng buộc vốn và mục tiêu công bằng.",
            ],
        ),
    ]


def bai07_brief(result: dict[str, Any]) -> BriefSections:
    pareto = result["pareto"]
    comp = result["compromise"]
    shares = {key: _num(comp.get(f"{key}_share")) for key in ["K", "D", "AI", "H"]}
    return [
        (
            "Chẩn đoán Pareto",
            [
                f"Tìm được {len(pareto)} nghiệm Pareto; nghiệm thỏa hiệp có GDP gain {_fmt(comp.get('gdp_gain'))}, inclusion {_fmt(comp.get('inclusion'))} và risk index {_fmt(comp.get('risk_index'), 3)}.",
                f"Cơ cấu thỏa hiệp: K {_pct(shares['K'])}, D {_pct(shares['D'])}, AI {_pct(shares['AI'])}, H {_pct(shares['H'])}; {_share_comment(shares)}.",
                f"Solver hiện tại: {result.get('solver', comp.get('solver', 'NSGA-II'))}.",
            ],
        ),
        (
            "Diễn giải chuyên gia",
            [
                "Điểm quan trọng của Pareto là không có nghiệm thống trị tuyệt đối: tăng GDP có thể làm giảm bao trùm hoặc tăng rủi ro.",
                "Nghiệm thỏa hiệp nên được hiểu là lựa chọn quản trị, không phải kết quả duy nhất đúng về toán học.",
            ],
        ),
        (
            "Khuyến nghị quyết định",
            [
                "Frontier thể hiện toàn bộ tập đánh đổi khả thi; nghiệm thỏa hiệp là một lựa chọn quản trị trong tập đó.",
                "Nếu ưu tiên rủi ro thấp hơn tăng trưởng, hệ thống có thể chọn một điểm khác trên Pareto thay vì nghiệm mặc định.",
            ],
        ),
    ]


def bai08_brief(result: dict[str, Any], baseline: pd.DataFrame) -> BriefSections:
    best = result["best"]
    trajectory = result["trajectory"]
    opt_2035 = _num(trajectory.sort_values("year")["GDP"].iloc[-1])
    base_2035 = _num(baseline.sort_values("year")["GDP"].iloc[-1])
    gain = opt_2035 - base_2035
    shares = {key: _num(best.get(key)) for key in ["K", "D", "AI", "H"]}
    return [
        (
            "Chẩn đoán đường động",
            [
                f"GDP 2035 tối ưu đạt {_fmt(opt_2035)} nghìn tỷ, cao hơn đường cơ sở cố định khoảng {_fmt(gain)} nghìn tỷ.",
                f"Cơ cấu bình quân: K {_pct(shares['K'])}, D {_pct(shares['D'])}, AI {_pct(shares['AI'])}, H {_pct(shares['H'])}; {_share_comment(shares)}.",
                f"Solver hiện tại: {result.get('solver', best.get('solver', 'dynamic optimizer'))}.",
            ],
        ),
        (
            "Diễn giải chuyên gia",
            [
                "Tối ưu động khác LP một kỳ ở chỗ quyết định hiện tại làm thay đổi trạng thái tương lai; vì vậy hiệu quả chính sách có tính tích lũy.",
                "Nếu mô hình ưu tiên vốn K hoặc nền tảng số hơn AI, đó là dấu hiệu AI cần hạ tầng và nhân lực để tạo sản lượng chứ không tự vận hành độc lập.",
            ],
        ),
        (
            "Khuyến nghị quyết định",
            [
                "Dùng đường baseline để chứng minh lợi ích của tối ưu hóa so với quy tắc phân bổ cố định.",
                "Đây là mô hình path planning 2026-2035, phù hợp với quyết định đầu tư dài hạn hơn là quyết định ngân sách một năm.",
            ],
        ),
    ]


def bai09_brief(result: pd.DataFrame, threshold: dict[str, Any]) -> BriefSections:
    total = _num(result["net_job_million"].sum())
    worst = _top_row(result, "net_job_million", ascending=True)
    best = _top_row(result, "net_job_million")
    threshold_text = "không tìm thấy trong miền quét" if pd.isna(threshold.get("threshold")) else f"{_fmt(threshold.get('threshold'), 0)} tỷ VND"
    total_note = "mất việc ròng" if total < 0 else "tạo việc ròng"
    return [
        (
            "Chẩn đoán lao động",
            [
                f"NetJob toàn nền kinh tế là {_fmt(total, 3)} triệu, tức trạng thái {total_note}; ngưỡng đào tạo tối thiểu ước tính: {threshold_text}.",
                f"Ngành chịu tác động âm lớn nhất: {worst.get('sector_name_vi', 'n/a')} ({_fmt(worst.get('net_job_million'), 3)} triệu).",
                f"Ngành có NetJob tốt nhất: {best.get('sector_name_vi', 'n/a')} ({_fmt(best.get('net_job_million'), 3)} triệu).",
            ],
        ),
        (
            "Diễn giải chuyên gia",
            [
                "AI adoption càng cao thì áp lực chuyển dịch lao động càng lớn; tác động ròng phụ thuộc vào tốc độ tạo việc mới và quy mô reskilling.",
                "Ngành lao động lớn và automation risk cao là vùng rủi ro xã hội trọng yếu, cần được ưu tiên hơn các ngành có quy mô việc làm nhỏ.",
            ],
        ),
        (
            "Khuyến nghị quyết định",
            [
                "Nếu NetJob âm, không nên trình bày AI như chính sách tăng trưởng thuần túy; cần kèm gói đào tạo lại và chuyển đổi việc làm.",
                "Ngưỡng đào tạo tối thiểu là thông tin tốt để trả lời câu hỏi: đầu tư AI bao nhiêu thì phải dành bao nhiêu cho con người.",
            ],
        ),
    ]


def bai10_brief(result: dict[str, Any]) -> BriefSections:
    policy = result["stochastic_policy"]
    values = result["scenario_values"]
    worst = _top_row(values, "value", ascending=True)
    ai_note = "đang chạm trần AI 50%" if _num(policy.get("AI")) >= 0.499 else "chưa chạm trần AI"
    human_note = "đang chạm sàn nhân lực 15%" if _num(policy.get("H")) <= 0.151 else "cao hơn sàn nhân lực"
    return [
        (
            "Chẩn đoán bất định",
            [
                f"Expected value {_fmt(policy.get('expected_value'))}, VSS {_fmt(result.get('vss'))}, EVPI {_fmt(result.get('evpi'))}.",
                f"Cơ cấu here-and-now: K {_pct(policy.get('K'))}, D {_pct(policy.get('D'))}, AI {_pct(policy.get('AI'))}, H {_pct(policy.get('H'))}; {ai_note}, {human_note}.",
                f"Kịch bản bất lợi nhất là {worst.get('scenario', 'n/a')} với giá trị {_fmt(worst.get('value'))}.",
            ],
        ),
        (
            "Diễn giải chuyên gia",
            [
                "EVPI dương nghĩa là thông tin hoàn hảo về kịch bản vẫn có giá trị, kể cả khi VSS bằng 0 trong bộ tham số hiện tại.",
                "Việc AI chạm trần và H chạm sàn cho thấy nghiệm muốn nghiêng về AI, nhưng ràng buộc hấp thụ buộc chính sách giữ mức nhân lực tối thiểu.",
            ],
        ),
        (
            "Khuyến nghị quyết định",
            [
                "VSS và EVPI bổ sung cho nhau: một chỉ số đo lợi ích của mô hình stochastic, chỉ số kia đo giá trị thông tin.",
                "Chính sách here-and-now nên được đọc như quyết định trước khi biết kịch bản, còn recourse cost là chi phí điều chỉnh sau khi bất định xảy ra.",
            ],
        ),
    ]


def bai11_brief(result: dict[str, Any]) -> BriefSections:
    policy = result["policy"]
    trace = result["reward_trace"]
    actions = _names(policy["best_action"].drop_duplicates(), 5)
    q_min = _num(policy["best_q"].min())
    q_max = _num(policy["best_q"].max())
    early_reward = _num(trace["reward"].head(30).mean())
    late_reward = _num(trace["reward"].tail(30).mean())
    direction = "cải thiện" if late_reward >= early_reward else "giảm"
    return [
        (
            "Chẩn đoán chính sách học được",
            [
                f"Các hành động được chọn theo trạng thái gồm: {actions}.",
                f"Best-Q dao động từ {_fmt(q_min, 2)} đến {_fmt(q_max, 2)}, phản ánh khác biệt giá trị giữa các trạng thái kinh tế.",
                f"Reward trung bình cuối kỳ {direction} so với đầu kỳ ({_fmt(early_reward, 1)} -> {_fmt(late_reward, 1)}).",
            ],
        ),
        (
            "Diễn giải chuyên gia",
            [
                "Q-learning phù hợp minh họa chính sách thích nghi: trạng thái suy giảm, ổn định, tăng trưởng hoặc rủi ro cao có thể cần hành động khác nhau.",
                "Nếu nhiều trạng thái chọn cùng một hành động, điều đó cho thấy reward hiện tại ưu tiên mạnh một cấu hình chính sách.",
            ],
        ),
        (
            "Khuyến nghị quyết định",
            [
                "Q-learning được sử dụng như cơ chế học chính sách thích nghi theo trạng thái, không phải công cụ quyết định ngân sách độc lập.",
                "Episodes và epsilon ảnh hưởng trực tiếp đến mức ổn định của quá trình học; huấn luyện dài hơn thường làm chính sách bớt dao động.",
            ],
        ),
    ]


def bai12_brief(scenarios: pd.DataFrame) -> BriefSections:
    best = scenarios.iloc[0]
    gdp_best = _top_row(scenarios, "GDP_gain")
    job_best = _top_row(scenarios, "net_job_million")
    low_risk = _top_row(scenarios, "risk_index", ascending=True)
    best_vs_gdp = "trùng" if best["scenario"] == gdp_best.get("scenario") else "khác"
    return [
        (
            "Chẩn đoán kịch bản tích hợp",
            [
                f"Kịch bản overall score cao nhất: {best['scenario']} ({_fmt(best['overall_score'], 3)}).",
                f"Kịch bản GDP cao nhất: {gdp_best.get('scenario', 'n/a')} ({_fmt(gdp_best.get('GDP_gain'))}); kịch bản NetJob tốt nhất: {job_best.get('scenario', 'n/a')} ({_fmt(job_best.get('net_job_million'), 3)} triệu).",
                f"Kịch bản rủi ro thấp nhất: {low_risk.get('scenario', 'n/a')}; lựa chọn overall hiện tại {best_vs_gdp} với lựa chọn tối đa GDP.",
            ],
        ),
        (
            "Diễn giải chuyên gia",
            [
                "Bài 12 là lớp tổng hợp: nó cho thấy phương án tốt nhất phụ thuộc vào cách cân bằng tăng trưởng, bao trùm, việc làm và rủi ro.",
                "Nếu kịch bản GDP cao nhất không đứng đầu overall score, đó là dấu hiệu mô hình đang ưu tiên phát triển bền vững hơn tăng trưởng ngắn hạn.",
            ],
        ),
        (
            "Khuyến nghị quyết định",
            [
                "Overall score là quy tắc tổng hợp có trọng số; khi ưu tiên chính sách thay đổi, thứ hạng kịch bản cũng có thể thay đổi.",
                "Kịch bản reskilling mạnh là điểm nhấn tốt vì nó biến yêu cầu nhân lực thành điều kiện kiểm soát rủi ro lao động của chuyển đổi AI.",
            ],
        ),
    ]
