from fastapi import APIRouter, Request, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from decimal import Decimal
import os, shutil, json
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.domain import Domain, DomainStatus
from app.models.server import Server, ServerStatus, ServerType
from app.models.customer import Customer
from app.services.ai_service import extract_text_from_file, parse_with_ai

router = APIRouter(prefix="/import", tags=["ai_import"])
templates = Jinja2Templates(directory="app/templates")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")


@router.get("/", response_class=HTMLResponse)
def import_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trang AI Import."""
    customers = db.query(Customer).order_by(Customer.name).all()
    return templates.TemplateResponse(
        "ai_import/index.html",
        {"request": request, "current_user": current_user, "customers": customers},
    )


@router.post("/upload")
async def process_import(
    request: Request,
    text_input: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Bước 1: Nhận file hoặc text → OCR (nếu ảnh) → gửi AI → trả về preview.
    """
    customers = db.query(Customer).order_by(Customer.name).all()

    # Lấy text từ file hoặc từ input trực tiếp
    if file and file.filename:
        tmp_dir = os.path.join(UPLOAD_DIR, "tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_path = os.path.join(tmp_dir, file.filename)
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        source_text = extract_text_from_file(tmp_path, file.filename)
        os.remove(tmp_path)  # Xoá file tạm
    elif text_input and text_input.strip():
        source_text = text_input.strip()
    else:
        return templates.TemplateResponse(
            "ai_import/index.html",
            {"request": request, "current_user": current_user, "customers": customers, "error": "Vui lòng upload file hoặc nhập text"},
        )

    # Gọi AI phân tích
    ai_result = parse_with_ai(source_text)

    return templates.TemplateResponse(
        "ai_import/preview.html",
        {
            "request": request,
            "current_user": current_user,
            "customers": customers,
            "ai_result": ai_result,
            "source_text": source_text,
            "ai_result_json": json.dumps(ai_result, ensure_ascii=False),
        },
    )


@router.post("/confirm")
async def confirm_import(
    request: Request,
    customer_id: int = Form(...),
    domains_json: str = Form("[]"),
    servers_json: str = Form("[]"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Bước 2: Admin đã review xong → lưu dữ liệu vào DB.
    """
    domains_data = json.loads(domains_json)
    servers_data = json.loads(servers_json)

    imported_domains = 0
    imported_servers = 0

    for d in domains_data:
        if not d.get("domain_name"):
            continue
        domain = Domain(
            customer_id=customer_id,
            domain_name=d.get("domain_name", ""),
            registrar=d.get("registrar"),
            expiry_date=_parse_date(d.get("expiry_date")),
            auto_renew=bool(d.get("auto_renew", False)),
            status=DomainStatus.active,
            notes=d.get("notes"),
        )
        db.add(domain)
        imported_domains += 1

    for s in servers_data:
        if not s.get("label"):
            continue
        server = Server(
            customer_id=customer_id,
            label=s.get("label", ""),
            provider=s.get("provider"),
            ip_address=s.get("ip_address"),
            type=_parse_server_type(s.get("type", "VPS")),
            expiry_date=_parse_date(s.get("expiry_date")),
            monthly_cost=Decimal(str(s["monthly_cost"])) if s.get("monthly_cost") else None,
            status=ServerStatus.active,
            notes=s.get("notes"),
        )
        db.add(server)
        imported_servers += 1

    db.commit()
    return templates.TemplateResponse(
        "ai_import/success.html",
        {
            "request": request,
            "current_user": current_user,
            "imported_domains": imported_domains,
            "imported_servers": imported_servers,
        },
    )


def _parse_date(value) -> date | None:
    if not value or value == "null":
        return None
    try:
        return date.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


def _parse_server_type(value: str) -> ServerType:
    mapping = {
        "VPS": ServerType.vps,
        "Shared Hosting": ServerType.shared,
        "Dedicated": ServerType.dedicated,
        "Cloud": ServerType.cloud,
    }
    return mapping.get(value, ServerType.vps)
