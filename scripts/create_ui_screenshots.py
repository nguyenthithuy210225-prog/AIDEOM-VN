# -*- coding: utf-8 -*-
"""Create GitHub-friendly UI preview screenshots for the AIDEOM-VN README."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshots"
FIG = ROOT / "outputs" / "figures"

W, H = 1600, 930
SIDEBAR_W = 280
BG = "#0b0f16"
SIDEBAR = "#242632"
PANEL = "#111827"
CARD = "#171b25"
BORDER = "#2b3342"
TEXT = "#f8fafc"
MUTED = "#9ca3af"
BLUE = "#7db7ff"
TEAL = "#11a38f"
GREEN = "#23c55e"
RED = "#ff4b5c"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


F = {
    "tiny": font(14),
    "small": font(17),
    "body": font(20),
    "label": font(18, True),
    "h2": font(30, True),
    "h1": font(46, True),
    "metric": font(38, True),
}


def rounded(draw: ImageDraw.ImageDraw, box, radius=8, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text(draw: ImageDraw.ImageDraw, xy, value, fill=TEXT, f="body", anchor=None):
    draw.text(xy, value, font=F[f], fill=fill, anchor=anchor)


def sidebar(draw: ImageDraw.ImageDraw, active: str):
    draw.rectangle((0, 0, SIDEBAR_W, H), fill=SIDEBAR)
    text(draw, (34, 70), "AIDEOM-VN", f="h2")
    text(draw, (34, 120), "Web app mô hình ra quyết định", fill=MUTED, f="small")
    text(draw, (34, 145), "phát triển kinh tế Việt Nam", fill=MUTED, f="small")
    pages = [
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
    y = 205
    for page in pages:
        selected = page == active
        draw.ellipse((32, y + 5, 47, y + 20), fill=RED if selected else SIDEBAR, outline="#596071")
        text(draw, (58, y), page, fill=TEXT if selected else "#d7dce7", f="small")
        y += 30
    draw.line((32, H - 170, SIDEBAR_W - 32, H - 170), fill="#555b68")
    text(draw, (34, H - 128), "Dự án:", fill=MUTED, f="small")
    text(draw, (88, H - 128), "aideom_vn", fill=GREEN, f="small")
    text(draw, (34, H - 88), "Nguồn: NSO/GSO, MoST,", fill=MUTED, f="small")
    text(draw, (34, H - 63), "MIC, MPI, WB, WIPO", fill=MUTED, f="small")


def chips(draw, x, y, items):
    for item in items:
        w = draw.textlength(item, font=F["tiny"]) + 18
        rounded(draw, (x, y, x + w, y + 26), 5, fill="#10231f")
        text(draw, (x + 9, y + 5), item, fill="#2dff8e", f="tiny")
        x += w + 8


def metric(draw, x, y, label, value, delta=None):
    text(draw, (x, y), label, f="label")
    text(draw, (x, y + 34), value, fill=BLUE, f="metric")
    if delta:
        rounded(draw, (x, y + 86, x + 78, y + 113), 14, fill="#0d4129")
        text(draw, (x + 10, y + 91), delta, fill="#37f583", f="tiny")


def table(draw, x, y, w, headers, rows, row_h=42):
    col_w = w // len(headers)
    rounded(draw, (x, y, x + w, y + row_h * (len(rows) + 1)), 8, fill=BG, outline=BORDER)
    draw.rectangle((x, y, x + w, y + row_h), fill=CARD)
    for i, h in enumerate(headers):
        text(draw, (x + i * col_w + 12, y + 12), h, fill=MUTED, f="small")
        if i:
            draw.line((x + i * col_w, y, x + i * col_w, y + row_h * (len(rows) + 1)), fill=BORDER)
    for r, row in enumerate(rows):
        yy = y + row_h * (r + 1)
        draw.line((x, yy, x + w, yy), fill=BORDER)
        for i, value in enumerate(row):
            text(draw, (x + i * col_w + 12, yy + 12), str(value), f="small")


def paste_chart(canvas: Image.Image, path: Path, box):
    if not path.exists():
        return
    chart = Image.open(path).convert("RGB")
    x1, y1, x2, y2 = box
    max_w, max_h = x2 - x1, y2 - y1
    chart.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    px = x1 + (max_w - chart.width) // 2
    py = y1 + (max_h - chart.height) // 2
    canvas.paste(chart, (px, py))


def base(active: str):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    sidebar(draw, active)
    return img, draw


def home():
    img, draw = base("Trang chủ")
    x = SIDEBAR_W + 70
    text(draw, (x, 60), "AIDEOM-VN DECISION LAB", fill=TEAL, f="label")
    text(draw, (x, 105), "AIDEOM-VN Policy Cockpit", f="h1")
    text(draw, (x, 170), "Không gian mô phỏng và tối ưu hóa quyết định phát triển kinh tế Việt Nam trong kỷ nguyên AI.", fill=MUTED, f="body")
    chips(draw, x, 215, ["Dữ liệu 2020-2025", "Tối ưu hóa", "Dashboard chính sách"])
    metric(draw, x, 285, "GDP 2025", "514.0 tỷ USD", "↑ 8.02%")
    metric(draw, x + 330, 285, "Kinh tế số/GDP", "19.5%", "↑ 1.2 điểm")
    metric(draw, x + 660, 285, "FDI giải ngân", "27.6 tỷ USD")
    metric(draw, x + 970, 285, "GDP/người", "5.026 USD")
    text(draw, (x, 460), "Bản đồ học phần", f="h2")
    table(draw, x, 510, 650, ["Cấp độ", "Phạm vi", "Trọng tâm"], [
        ["Dễ", "Bài 1-3", "Cobb-Douglas, LP đơn giản"],
        ["Trung bình", "Bài 4-6", "LP ngành-vùng, MIP, TOPSIS"],
        ["Khá khó", "Bài 7-9", "Pareto, tối ưu động, lao động & AI"],
        ["Khó", "Bài 10-12", "Stochastic SP, Q-learning"],
    ], 43)
    paste_chart(img, FIG / "bai12_scenario_comparison.png", (x + 720, 430, W - 60, 820))
    return img


def bai01():
    img, draw = base("Bài 1 - Cobb-Douglas + AI")
    x = SIDEBAR_W + 70
    text(draw, (x, 60), "AIDEOM-VN DECISION LAB", fill=TEAL, f="label")
    text(draw, (x, 105), "Bài 1 - Hàm sản xuất Cobb-Douglas mở rộng", f="h1")
    text(draw, (x, 170), "Ước lượng TFP, dự báo GDP, phân rã tăng trưởng và mô phỏng kịch bản 2030.", fill=MUTED, f="body")
    chips(draw, x, 215, ["Cobb-Douglas", "Growth accounting", "MAPE"])
    text(draw, (x + 430, 270), "Y = A x K^alpha x L^beta x D^gamma x AI^delta x H^theta", f="body")
    metric(draw, x, 330, "TFP trung bình", "30.94")
    metric(draw, x + 420, 330, "MAPE", "6.42%")
    metric(draw, x + 840, 330, "GDP 2030", "14.502,7 nghìn tỷ")
    table(draw, x, 460, 760, ["year", "GDP_2030", "K_2030", "AI_2030"], [["2030", "14502.667", "34660.042", "100"]], 48)
    rounded(draw, (x, 560, x + 760, 690), 8, fill="#f8fafc", outline="#d2d7e0")
    text(draw, (x + 22, 585), "Tác nhân phân tích kết quả", fill="#0f172a", f="label")
    text(draw, (x + 22, 625), "TFP tăng ổn định; kịch bản 2030 phản ánh vai trò bổ trợ", fill="#0f172a", f="small")
    text(draw, (x + 22, 650), "của kinh tế số, AI và nhân lực số trong tăng trưởng.", fill="#0f172a", f="small")
    paste_chart(img, FIG / "bai01_actual_vs_predicted_gdp.png", (x + 810, 450, W - 60, 820))
    return img


def bai05():
    img, draw = base("Bài 5 - MIP 15 dự án")
    x = SIDEBAR_W + 70
    text(draw, (x, 60), "AIDEOM-VN DECISION LAB", fill=TEAL, f="label")
    text(draw, (x, 105), "Bài 5 - MIP lựa chọn dự án", f="h1")
    text(draw, (x, 170), "Chọn tập dự án chuyển đổi số dưới ngân sách, rủi ro và ràng buộc logic.", fill=MUTED, f="body")
    chips(draw, x, 215, ["MIP", "Binary decision", "Knapsack"])
    text(draw, (x, 270), "Ngân sách dự án (tỷ VND)", f="label")
    draw.line((x, 315, W - 90, 315), fill="#3b414e", width=5)
    draw.line((x, 315, x + 760, 315), fill=RED, width=5)
    draw.ellipse((x + 750, 305, x + 770, 325), fill=RED)
    metric(draw, x, 370, "Lợi ích NPV", "133.300,0")
    metric(draw, x + 470, 370, "Chi phí", "76.600,0")
    metric(draw, x + 920, 370, "Rủi ro", "145/145")
    table(draw, x, 500, 1180, ["project_id", "project_name", "category", "selected"], [
        ["P02", "Trung tâm AI quốc gia", "AI", "1"],
        ["P04", "Cloud chính phủ", "Infrastructure", "1"],
        ["P08", "Bản dẫn và thiết kế chip", "AI", "1"],
        ["P12", "Logistics thông minh", "Infrastructure", "1"],
    ], 45)
    rounded(draw, (x, 735, W - 90, 835), 8, fill="#f8fafc", outline="#d2d7e0")
    text(draw, (x + 22, 758), "Tác nhân phân tích kết quả", fill="#0f172a", f="label")
    text(draw, (x + 22, 795), "Danh mục ưu tiên các dự án có lợi ích cao nhưng vẫn nằm trong trần rủi ro.", fill="#0f172a", f="small")
    return img


def bai12():
    img, draw = base("Bài 12 - AIDEOM tích hợp")
    x = SIDEBAR_W + 70
    text(draw, (x, 60), "AIDEOM-VN DECISION LAB", fill=TEAL, f="label")
    text(draw, (x, 105), "Bài 12 - AIDEOM-VN tích hợp", f="h1")
    text(draw, (x, 170), "Dashboard tổng hợp 6 module và so sánh các kịch bản chính sách.", fill=MUTED, f="body")
    chips(draw, x, 215, ["Integrated dashboard", "Scenario comparison", "AIDEOM-VN"])
    metric(draw, x, 280, "Kịch bản tốt nhất", "S4. Bao trùm số")
    metric(draw, x + 520, 280, "Overall score", "0.800")
    metric(draw, x + 900, 280, "NetJob tốt nhất", "-1.536 triệu")
    table(draw, x, 400, 1180, ["scenario", "GDP_gain", "inclusion", "risk_index", "overall"], [
        ["S4. Bao trùm số", "77440", "60880", "6.4", "0.80"],
        ["S5. Tối ưu cân bằng", "81800", "50600", "17.7", "0.65"],
        ["S2. Số hóa nhanh", "81000", "51680", "17.8", "0.55"],
    ], 45)
    paste_chart(img, FIG / "bai12_scenario_comparison.png", (x + 120, 565, W - 140, 900))
    return img


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    screens = {
        "01_home_dashboard.png": home(),
        "02_bai01_cobb_douglas.png": bai01(),
        "03_bai05_project_mip.png": bai05(),
        "04_bai12_integrated_dashboard.png": bai12(),
    }
    for filename, image in screens.items():
        image.save(OUT / filename, quality=95)
        print(OUT / filename)


if __name__ == "__main__":
    main()
