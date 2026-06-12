# Hướng Dẫn Sử Dụng Web App AIDEOM-VN

## 1. Chạy ứng dụng

Mở PowerShell tại thư mục dự án:

```powershell
cd D:\Work\BaiTap\aideom_vn
.\run_app.bat
```

Sau đó mở trình duyệt tại:

```text
http://localhost:8501
```

## 2. Cấu trúc app

Web app có 13 mục điều hướng:

- Trang chủ: KPI và trạng thái dữ liệu.
- Bài 1 đến Bài 12: mỗi bài có tham số, bảng kết quả, biểu đồ và Policy Brief.

## 3. Sinh output CSV

```powershell
cd D:\Work\BaiTap\aideom_vn
python scripts\generate_outputs.py
```

Kết quả được lưu tại:

```text
outputs\tables\
```

## 4. Sinh biểu đồ PNG cho báo cáo

Sau khi sinh CSV, chạy:

```powershell
cd D:\Work\BaiTap\aideom_vn
python scripts\generate_figures.py
```

Kết quả được lưu tại:

```text
outputs\figures\
```

File `outputs\figures\FIGURE_INDEX.md` ghi rõ từng hình lấy từ CSV nào và model nào.

## 4b. Lưu biểu đồ trực tiếp từ web sau khi chỉnh tham số

Trong mỗi trang bài tập trên web app có nút:

```text
Lưu figures trang hiện tại
```

Sau khi chỉnh slider/tham số, bấm nút này để lưu các biểu đồ đang hiển thị theo đúng trạng thái hiện tại.

File được lưu tại:

```text
outputs\figures\web_exports\<ma_bai>\
```

Mỗi biểu đồ được lưu thành hai dạng:

- `.png`: dùng để chèn vào Word/PDF.
- `.html`: giữ biểu đồ tương tác để xem lại trong trình duyệt.

Cách này phù hợp khi muốn báo cáo phản ánh đúng một kịch bản tham số tùy chỉnh, thay vì bộ hình mặc định do `generate_figures.py` tạo.

## 5. Đóng gói bài nộp

```powershell
cd D:\Work\BaiTap\aideom_vn
.\package_app.bat
```

File nộp sẽ được tạo tại:

```text
aideom_vn_submission.zip
```

## 6. Ghi chú triển khai

- App chạy local, không cần Google Colab.
- Gemini/Grok chưa được gọi API thật; phần tác nhân phân tích được triển khai bằng Policy Brief nội bộ để bảo đảm demo ổn định.
- Một số bài nâng cao dùng tham số mô phỏng nội bộ vì đề PDF không kèm bảng phụ chi tiết cho dự án, kịch bản stochastic và MDP.
