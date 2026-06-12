# Báo Cáo Tóm Tắt AIDEOM-VN

## 1. Mục tiêu

Dự án xây dựng web app AIDEOM-VN theo phương án 3: một dashboard ra quyết định có 12 menu tương ứng 12 bài trong đề cuối kỳ. Mỗi bài cho phép điều chỉnh tham số, chạy mô hình Python, xem bảng kết quả, biểu đồ và phần phân tích chính sách tự động.

## 2. Dữ liệu

Ba bộ dữ liệu được sử dụng:

- `vietnam_macro_2020_2025.csv`
- `vietnam_sectors_2024.csv`
- `vietnam_regions_2024.csv`

Dữ liệu phản ánh GDP, FDI, xuất nhập khẩu, kinh tế số, 10 ngành kinh tế và 6 vùng kinh tế xã hội Việt Nam.

## 3. Cấu trúc chức năng

| Bài | Mô hình/kỹ thuật | Output chính |
|---|---|---|
| 1 | Cobb-Douglas mở rộng | TFP, MAPE, dự báo GDP 2030 |
| 2 | Linear Programming | Phân bổ ngân sách, shadow price, sensitivity |
| 3 | Priority Index | Xếp hạng 10 ngành, độ nhạy trọng số |
| 4 | LP ngành-vùng | Phân bổ vùng-ngành-hạng mục |
| 5 | MIP PuLP/CBC | Danh mục dự án được chọn |
| 6 | TOPSIS | Xếp hạng 6 vùng ưu tiên AI |
| 7 | pymoo NSGA-II/Pareto | Tập nghiệm Pareto và nghiệm thỏa hiệp |
| 8 | Tối ưu động liên thời gian | Quỹ đạo GDP 2026-2035 |
| 9 | Mô phỏng lao động | JobLoss, JobCreation, NetJob |
| 10 | Pyomo Stochastic Programming | Expected value, VSS, EVPI |
| 11 | Q-learning | Q-table và chính sách thích nghi |
| 12 | Dashboard tích hợp | So sánh 6 kịch bản và thiết kế 6 module |

## 4. Thiết kế web app

Ứng dụng được xây bằng Streamlit và Plotly. Lõi tính toán nằm trong `src/aideom_vn`, còn `dashboard/app.py` chỉ đảm nhiệm giao diện và gọi hàm mô hình.

Mỗi bài có cấu trúc:

1. Tên bài, kỹ thuật, mô hình.
2. Tham số có thể chỉnh.
3. Bảng kết quả.
4. Biểu đồ.
5. Policy Brief phân tích kết quả.
6. Nút tải CSV ở các bảng chính.

## 5. Biểu đồ phục vụ báo cáo

Các biểu đồ tĩnh phục vụ Word/PDF được sinh bằng:

```powershell
python scripts\generate_outputs.py
python scripts\generate_figures.py
```

Hình PNG nằm trong `outputs/figures/`. File `FIGURE_INDEX.md` trong cùng thư mục ghi rõ từng hình lấy từ output CSV nào và model nào. Cách này bảo đảm hình trong báo cáo khớp với bảng output và web app.

Ngoài bộ hình mặc định, web app còn hỗ trợ lưu biểu đồ trực tiếp từ từng trang bài tập bằng nút `Lưu figures trang hiện tại`. Khi người dùng chỉnh tham số rồi bấm nút này, hệ thống lưu biểu đồ theo đúng trạng thái hiện tại vào `outputs/figures/web_exports/<ma_bai>/` dưới hai định dạng PNG và HTML. Tính năng này giúp báo cáo có thể dùng đúng kịch bản tham số đã chọn trong lúc phân tích.

## 6. Ghi chú học thuật

Các bài có dữ liệu trực tiếp từ CSV được tính theo dữ liệu gốc. Các bài cần thông tin không có trong CSV, ví dụ danh sách 15 dự án, kịch bản stochastic, trạng thái-hành động của Q-learning, được bổ sung bằng bộ tham số mô phỏng nội bộ nhất quán với tinh thần đề bài. Khi viết bản Word/PDF cuối, cần ghi rõ đây là tham số giả định phục vụ thực hành.

Các giả định đã được đưa trực tiếp vào web app ở các bài có tham số mô phỏng:

- Bài 4: hệ số vùng-ngành-hạng mục, sàn/trần phân bổ theo vùng và trần theo ngành.
- Bài 5: danh mục 15 dự án, cost/benefit/risk và ràng buộc logic.
- Bài 7: hàm mục tiêu Pareto, ràng buộc tỷ trọng K/D/AI/H và cách chọn nghiệm thỏa hiệp.
- Bài 8: mô hình tối ưu liên thời gian formal, ưu tiên CVXPY và dùng SLSQP trong venv hiện tại.
- Bài 10: kịch bản stochastic, recourse cost, giới hạn AI tối đa 50%, nhân lực số tối thiểu 15% và vai trò của `comparison_grid`.
- Bài 11: trạng thái MDP, action set và reward mô phỏng.

Điểm đã rà soát thêm ngày 31/05/2026: dự báo Bài 1 dùng giả định lao động tăng 0,6%/năm thay vì 6%/năm để tránh phóng đại lực lượng lao động 2030; Bài 12 bổ sung S6 Reskilling mạnh để minh họa điều kiện đưa NetJob về dương, còn S5 là phương án so sánh cân bằng khi ưu tiên tăng trưởng hơn bao trùm.

## Cập nhật học thuật sau audit Bài 2/8/10/12

- Bài 2 dùng PuLP/CBC làm solver LP mặc định và ghi rõ nguồn shadow price là dual `constraint pi` của CBC; SciPy/HiGHS giữ vai trò fallback.
- Bài 8 đã chuyển sang tối ưu liên thời gian formal: biến quyết định là tỷ trọng K, D, AI, H theo từng năm 2026-2035; mục tiêu là quỹ đạo GDP chiết khấu. Nếu môi trường có CVXPY thì dùng CVXPY, nếu không dùng `scipy.SLSQP_intertemporal_NLP`.
- Bài 10 cần diễn giải riêng khi `VSS = 0`: trong bộ tham số hiện tại chính sách expected-value trùng hoặc không kém nghiệm stochastic; `EVPI > 0` vẫn hợp lý vì thông tin hoàn hảo cho phép chọn chính sách riêng theo từng kịch bản.
- Bài 12 bổ sung `S6. Reskilling manh`, dùng quỹ đào tạo tăng cường để tạo một phương án NetJob dương. Các kịch bản còn lại vẫn có thể được trình bày như cảnh báo rằng đầu tư AI/số hóa không tự bảo đảm việc làm ròng dương nếu thiếu reskilling.

## 7. Kết luận

Bản web app đáp ứng phương án 3: có giao diện, 12 menu, tính toán trực tiếp, biểu đồ, tác nhân phân tích nội bộ, hướng dẫn sử dụng và khả năng đóng gói thành file zip để nộp.
