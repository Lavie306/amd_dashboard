# AMD-IMS — Internal Management System

Hệ thống quản lý nội bộ của **AMD AI Solutions Co., Ltd.**

## Tính năng

- **Dashboard** — Cảnh báo domain/server sắp hết hạn (30 ngày)
- **Khách hàng** — CRUD quản lý khách hàng cá nhân & doanh nghiệp
- **Dự án** — Quản lý dự án, hợp đồng, các đợt thanh toán
- **Domain & Server** — Theo dõi hạn đăng ký, Vault lưu credentials bảo mật
- **Managed IT** — Quản lý gói dịch vụ IT theo tháng/năm
- **Hóa đơn VAT** — Upload PDF, tính VAT tự động
- **Sản phẩm** — Danh mục sản phẩm nội bộ
- **AI Import** — Nhập dữ liệu tự động bằng Gemini / Groq AI + OCR

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI (Python) |
| Database | SQLite + SQLAlchemy ORM |
| Templates | Jinja2 |
| Auth | Session-based (cookie) |
| AI | Google Gemini 2.0 Flash / Groq LLaMA |
| OCR | Tesseract (optional) |

## Cài đặt

```bash
# 1. Clone repo
git clone https://github.com/Lavie306/amd_dashboard.git
cd amd_dashboard

# 2. Tạo virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Cài dependencies
pip install -r requirements.txt

# 4. Cấu hình .env
copy .env.example .env
# Chỉnh sửa .env với SECRET_KEY và API keys

# 5. Khởi tạo database
python init_db.py

# 6. Chạy server
uvicorn app.main:app --reload --port 8000
```

Truy cập: http://localhost:8000  
Login mặc định: `admin` / `admin123`

## Cấu trúc thư mục

```
amd-ims/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # SQLAlchemy config
│   ├── dependencies.py      # Auth guard
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # Route handlers
│   ├── services/            # Business logic (AI, Expiry)
│   └── templates/           # Jinja2 HTML templates
├── static/
│   └── css/style.css        # Design system
├── init_db.py               # DB init + admin user
├── requirements.txt
└── .env.example
```

## Biến môi trường (.env)

```env
DATABASE_URL=sqlite:///./amd_ims.db
SECRET_KEY=your-secret-key-here
AI_PROVIDER=gemini          # hoặc: groq
GEMINI_API_KEY=             # Google AI Studio (miễn phí)
GROQ_API_KEY=               # Groq Console (miễn phí)
UPLOAD_DIR=uploads
```
