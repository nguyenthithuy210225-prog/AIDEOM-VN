# -*- coding: utf-8 -*-
"""Create a short defense/demo video script for AIDEOM-VN."""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "KICH_BAN_VIDEO_GIOI_THIEU_AIDEOM_VN.docx"
FONT = "Arial"
DARK = RGBColor(17, 24, 39)
TEAL = RGBColor(0, 128, 112)
GRAY = RGBColor(75, 85, 99)
BORDER = "CBD5E1"


def _set_run_font(run):
    run.font.name = FONT
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.rFonts
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for key in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(key), FONT)


def _set_style_font(style, size=None, bold=None, color=None):
    style.font.name = FONT
    if size is not None:
        style.font.size = Pt(size)
    if bold is not None:
        style.font.bold = bold
    if color is not None:
        style.font.color.rgb = color
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.rFonts
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for key in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(key), FONT)


def add_run(paragraph, text, size=10.5, bold=False, color=DARK, italic=False):
    run = paragraph.add_run(text)
    _set_run_font(run)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color
    return run


def border_table(table):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        elem = borders.find(qn(f"w:{edge}"))
        if elem is None:
            elem = OxmlElement(f"w:{edge}")
            borders.append(elem)
        elem.set(qn("w:val"), "single")
        elem.set(qn("w:sz"), "4")
        elem.set(qn("w:space"), "0")
        elem.set(qn("w:color"), BORDER)


def shade_cell(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell(cell, text, bold=False, fill=None, color=DARK):
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
    if fill:
        shade_cell(cell, fill)
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(0)
    add_run(paragraph, text, size=9.3, bold=bold, color=color)


def add_heading(doc, text, level=1):
    paragraph = doc.add_paragraph()
    paragraph.style = f"Heading {level}"
    paragraph.paragraph_format.space_before = Pt(8)
    paragraph.paragraph_format.space_after = Pt(5)
    add_run(paragraph, text, size=17 if level == 1 else 12.5, bold=True, color=TEAL if level == 1 else DARK)


def add_body(doc, text):
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(5)
    paragraph.paragraph_format.line_spacing = 1.1
    add_run(paragraph, text, size=10.4)


def add_bullet(doc, text):
    paragraph = doc.add_paragraph(style="List Bullet")
    paragraph.paragraph_format.space_after = Pt(2)
    add_run(paragraph, text, size=10.1)


def add_scene(doc, title, duration, action, script):
    add_heading(doc, title, 2)
    table = doc.add_table(rows=3, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    border_table(table)
    rows = [
        ("Thời lượng", duration),
        ("Thao tác quay màn hình", action),
        ("Lời thoại", script),
    ]
    for idx, (label, value) in enumerate(rows):
        set_cell(table.rows[idx].cells[0], label, bold=True, fill="E0F2F1")
        set_cell(table.rows[idx].cells[1], value)
    for row in table.rows:
        tr_pr = row._tr.get_or_add_trPr()
        tr_pr.append(OxmlElement("w:cantSplit"))
    doc.add_paragraph()


def setup_doc():
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.65)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)
    for style_name, size, bold, color in [
        ("Normal", 10.4, False, DARK),
        ("Heading 1", 17, True, TEAL),
        ("Heading 2", 12.5, True, DARK),
        ("List Bullet", 10.1, False, DARK),
    ]:
        _set_style_font(doc.styles[style_name], size, bold, color)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(footer, "AIDEOM-VN Decision Lab | Kịch bản video demo", size=8.5, color=GRAY)
    return doc


def main():
    doc = setup_doc()

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_before = Pt(24)
    add_run(title, "KỊCH BẢN VIDEO GIỚI THIỆU DỰ ÁN", size=20, bold=True, color=DARK)
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(subtitle, "AIDEOM-VN Policy Cockpit - thời lượng gợi ý 4 đến 5 phút", size=12, color=GRAY)

    add_heading(doc, "Mục tiêu video", 1)
    for item in [
        "Giới thiệu ngắn gọn mục tiêu, cấu trúc và điểm nổi bật của web app.",
        "Trình diễn được các nhóm chức năng chính: dự báo, tối ưu hóa, Pareto và dashboard tích hợp.",
        "Làm rõ tác nhân phân tích kết quả và cách kết quả thay đổi theo tham số.",
        "Kết thúc bằng output, báo cáo và khả năng đóng gói nộp.",
    ]:
        add_bullet(doc, item)

    add_heading(doc, "Chuẩn bị trước khi quay", 1)
    for item in [
        "Mở sẵn thư mục dự án và trình duyệt tại http://localhost:8501.",
        "Nếu chưa chạy app: mở file run_app.bat hoặc chạy lệnh streamlit run dashboard/app.py.",
        "Phóng to trình duyệt khoảng 100-110%, ẩn các tab không cần thiết để video gọn.",
        "Khi quay, thao tác chậm, mỗi lần kéo tham số dừng 1-2 giây để người xem thấy kết quả cập nhật.",
    ]:
        add_bullet(doc, item)

    add_heading(doc, "Kịch bản theo cảnh", 1)
    add_scene(
        doc,
        "Cảnh 1 - Mở đầu dự án",
        "20 giây",
        "Mở thư mục dự án hoặc mở sẵn web app tại localhost:8501. Đưa màn hình về trang chủ.",
        "Xin chào thầy cô, em xin giới thiệu dự án AIDEOM-VN Policy Cockpit. Đây là web app mô phỏng và tối ưu hóa các mô hình ra quyết định phục vụ phân tích phát triển kinh tế Việt Nam trong bối cảnh chuyển đổi số và AI. Dự án gồm 12 bài tương ứng với 12 mô hình hoặc nhóm chức năng trong đề cuối kỳ.",
    )
    add_scene(
        doc,
        "Cảnh 2 - Trang chủ và dữ liệu tổng quan",
        "40 giây",
        "Ở Trang chủ, chỉ vào các KPI GDP, kinh tế số/GDP, FDI, GDP/người. Sau đó chỉ vào biểu đồ chuẩn hóa 2020 = 100.",
        "Ở trang chủ, hệ thống hiển thị tổng quan dữ liệu đầu vào như GDP, tỷ trọng kinh tế số, FDI giải ngân và GDP/người. Biểu đồ bên phải chuẩn hóa các chỉ tiêu về năm gốc 2020 bằng 100 để so sánh tốc độ thay đổi tương đối giữa GDP, xuất khẩu và FDI. Cách này giúp tránh sai lệch do các chỉ tiêu có đơn vị và quy mô khác nhau.",
    )
    doc.add_page_break()
    add_scene(
        doc,
        "Cảnh 3 - Bài 1: Cobb-Douglas mở rộng",
        "50 giây",
        "Chọn Bài 1. Lần lượt bấm các tab TFP, Dự báo, Đóng góp tăng trưởng, Kịch bản 2030. Nếu có thanh tham số, kéo nhẹ D/AI/H rồi dừng.",
        "Bài 1 sử dụng hàm sản xuất Cobb-Douglas mở rộng, có thêm các yếu tố kinh tế số, AI và nhân lực số. Hệ thống tính TFP, sai số MAPE, dự báo GDP và phân rã đóng góp tăng trưởng. Khi thay đổi tham số kịch bản, kết quả GDP dự báo và phần phân tích phía dưới cập nhật theo. Đây là điểm khác với báo cáo tĩnh vì người dùng có thể kiểm tra độ nhạy trực tiếp trên giao diện.",
    )
    add_scene(
        doc,
        "Cảnh 4 - Bài 5: Tối ưu lựa chọn dự án",
        "50 giây",
        "Chọn Bài 5. Kéo Ngân sách dự án hoặc Trần rủi ro. Chỉ vào bảng dự án được chọn và các KPI lợi ích, chi phí, rủi ro.",
        "Bài 5 là mô hình MIP lựa chọn danh mục dự án chuyển đổi số. Đầu vào gồm ngân sách, lợi ích kỳ vọng, chi phí, rủi ro và các ràng buộc logic giữa dự án. Khi thay đổi ngân sách hoặc trần rủi ro, hệ thống tính lại danh mục dự án được chọn. Kết quả cho thấy tổng lợi ích, tổng chi phí, tổng rủi ro và danh sách dự án tối ưu.",
    )
    add_scene(
        doc,
        "Cảnh 5 - Bài 7: Pareto đa mục tiêu",
        "50 giây",
        "Chọn Bài 7. Chỉ vào biểu đồ Pareto frontier và bảng nghiệm thỏa hiệp.",
        "Bài 7 sử dụng tối ưu đa mục tiêu Pareto. Thay vì chỉ tối đa hóa một mục tiêu, mô hình xem xét đồng thời tăng trưởng GDP, bao trùm xã hội, xanh hóa và an ninh dữ liệu. Biểu đồ Pareto thể hiện các nghiệm đánh đổi. Không có một nghiệm tuyệt đối tốt nhất cho mọi mục tiêu, mà người ra quyết định cần chọn nghiệm phù hợp với ưu tiên chính sách.",
    )
    add_scene(
        doc,
        "Cảnh 6 - Bài 12: Dashboard tích hợp",
        "40 giây",
        "Chọn Bài 12. Chỉ vào bảng so sánh kịch bản và biểu đồ cột/radar nếu đang hiển thị.",
        "Bài 12 tổng hợp các logic chính thành dashboard tích hợp. Hệ thống so sánh nhiều kịch bản chính sách như truyền thống, số hóa nhanh, AI dẫn dắt, bao trùm số và tối ưu cân bằng. Mỗi kịch bản có các chỉ tiêu như GDP gain, mức bao trùm, rủi ro, tác động việc làm và điểm tổng hợp.",
    )
    doc.add_page_break()
    add_scene(
        doc,
        "Cảnh 7 - Tác nhân phân tích kết quả",
        "40 giây",
        "Cuộn xuống cuối một bài bất kỳ, tốt nhất Bài 1 hoặc Bài 12. Chỉ vào khung Tác nhân phân tích kết quả.",
        "Một điểm riêng của web app là mỗi bài đều có tác nhân phân tích kết quả ở cuối trang. Tác nhân này đọc kết quả hiện tại của mô hình, sau đó diễn giải theo các lớp: chẩn đoán dữ liệu, diễn giải chuyên gia, hàm ý chính sách và lưu ý rủi ro. Khi người dùng thay đổi tham số, phần phân tích cũng thay đổi theo kết quả hiện tại.",
    )
    add_scene(
        doc,
        "Cảnh 8 - Output và báo cáo",
        "30 giây",
        "Mở nhanh thư mục outputs/tables, outputs/figures và reports. Chỉ vào file báo cáo Word và file zip nếu cần.",
        "Ngoài giao diện web, dự án còn lưu kết quả thành các bảng CSV trong outputs/tables và biểu đồ PNG trong outputs/figures để dùng cho báo cáo. Thư mục reports có báo cáo Word giới thiệu dự án và hướng dẫn sử dụng. Dự án cũng có file đóng gói aideom_vn_submission.zip gồm source code, dữ liệu, output, báo cáo và hướng dẫn chạy.",
    )
    add_scene(
        doc,
        "Cảnh 9 - Kết thúc",
        "20 giây",
        "Quay lại Trang chủ hoặc Bài 12. Dừng màn hình ở dashboard tổng quan.",
        "Tóm lại, AIDEOM-VN đáp ứng yêu cầu phương án web app: có 12 menu cho 12 bài, tính toán trực tiếp, chỉnh tham số, hiển thị bảng, biểu đồ, lưu output và có tác nhân phân tích kết quả. Dự án có thể chạy hoàn toàn local, không phụ thuộc Colab, và phù hợp để trình bày như một hệ thống hỗ trợ ra quyết định. Em xin kết thúc phần giới thiệu tại đây. Em cảm ơn thầy cô đã theo dõi.",
    )

    add_heading(doc, "Lưu ý khi thu âm", 1)
    for item in [
        "Nói chậm, rõ, không đọc quá nhanh khi chuyển cảnh.",
        "Nếu video cần ngắn hơn 4 phút, có thể bỏ Cảnh 4 hoặc Cảnh 5, nhưng nên giữ Cảnh 7 về tác nhân phân tích kết quả.",
        "Khi có lỗi nhỏ trong thao tác, không cần quay lại từ đầu; dừng 1 giây rồi tiếp tục thao tác bình tĩnh.",
    ]:
        add_bullet(doc, item)

    OUT.parent.mkdir(exist_ok=True)
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
