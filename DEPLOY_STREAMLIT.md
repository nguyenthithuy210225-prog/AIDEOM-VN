# Hướng dẫn triển khai AIDEOM-VN lên Streamlit Community Cloud

## 1. Điều kiện bắt buộc

- Code phải nằm trong một GitHub repository public hoặc repository mà tài khoản Streamlit có quyền truy cập.
- Repository nên có cấu trúc root như sau, không lồng thêm thư mục `aideom_vn` bên ngoài:

```text
repo/
├── dashboard/
│   ├── app.py
│   └── requirements.txt
├── data/
├── docs/
├── outputs/
├── reports/
├── src/
├── README.md
└── requirements.txt
```

## 2. Thông tin cần điền khi deploy

Vào:

```text
https://share.streamlit.io
```

Chọn **Create app** hoặc **New app**, sau đó điền:

```text
Repository: nguyenthithuy210225-prog/C-c-m-h-nh-ra-quy-t-nh-
Branch: main
Main file path: dashboard/app.py
Python version: 3.11
```

Nếu repository đang bị lồng thư mục, ví dụ:

```text
repo/aideom_vn/dashboard/app.py
```

thì `Main file path` phải là:

```text
aideom_vn/dashboard/app.py
```

Tuy nhiên cách chuẩn hơn là upload lại để `dashboard`, `src`, `data`, `README.md` nằm ngay ở root repo.

## 3. Vì sao có `dashboard/requirements.txt`?

Streamlit Cloud sẽ chạy app từ file `dashboard/app.py`. Vì vậy file `dashboard/requirements.txt` được dùng riêng cho môi trường deploy, chỉ gồm thư viện cần để chạy web app. File root `requirements.txt` giữ cho bản local đầy đủ hơn, bao gồm thư viện tạo báo cáo, kiểm thử và notebook.

## 4. Sau khi deploy

Khi build xong, Streamlit sẽ cấp link dạng:

```text
https://ten-app-cua-ban.streamlit.app
```

Bạn chỉ cần gửi link này cho người khác. Nếu repo public thì app có thể xem công khai theo link.

## 5. Nếu deploy lỗi

- Kiểm tra `Main file path` có đúng là `dashboard/app.py` không.
- Kiểm tra code đã nằm trên GitHub branch `main`.
- Mở phần log của Streamlit Cloud để xem thiếu package nào.
- Nếu vừa sửa GitHub, bấm **Reboot app** hoặc **Rerun** trên Streamlit Cloud.
