from fastapi import APIRouter, Request, Form, Depends, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from datetime import date
import os, shutil
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.invoice import Invoice
from app.models.customer import Customer
from app.models.project import Project

router = APIRouter(prefix="/invoices", tags=["invoices"])
templates = Jinja2Templates(directory="app/templates")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")


@router.get("/", response_class=HTMLResponse)
def list_invoices(
    request: Request,
    q: Optional[str] = None,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Invoice)
    if q:
        query = query.filter(Invoice.invoice_number.ilike(f"%{q}%"))
    if customer_id:
        query = query.filter(Invoice.customer_id == customer_id)
    invoices = query.order_by(Invoice.issue_date.desc()).all()
    customers = db.query(Customer).order_by(Customer.name).all()
    return templates.TemplateResponse(
        "invoices/list.html",
        {"request": request, "current_user": current_user, "invoices": invoices, "customers": customers, "q": q, "customer_id": customer_id},
    )


@router.get("/new", response_class=HTMLResponse)
def new_invoice_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customers = db.query(Customer).order_by(Customer.name).all()
    projects = db.query(Project).order_by(Project.name).all()
    return templates.TemplateResponse(
        "invoices/form.html",
        {"request": request, "current_user": current_user, "invoice": None, "customers": customers, "projects": projects},
    )


@router.post("/")
def create_invoice(
    customer_id: int = Form(...),
    project_id: Optional[str] = Form(None),
    invoice_number: str = Form(...),
    issue_date: str = Form(...),
    amount: str = Form(...),
    vat: str = Form("10"),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    amt = Decimal(amount)
    v = Decimal(vat)
    total = amt * (1 + v / 100)
    proj_id = int(project_id) if project_id and project_id.strip() else None
    invoice = Invoice(
        customer_id=customer_id,
        project_id=proj_id,
        invoice_number=invoice_number,
        issue_date=date.fromisoformat(issue_date) if issue_date and issue_date.strip() else date.today(),
        amount=amt,
        vat=v,
        total=total,
        notes=notes,
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return RedirectResponse(url=f"/invoices/{invoice.id}", status_code=302)


@router.get("/{invoice_id}", response_class=HTMLResponse)
def invoice_detail(
    invoice_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Không tìm thấy hóa đơn")
    return templates.TemplateResponse(
        "invoices/detail.html",
        {"request": request, "current_user": current_user, "invoice": invoice},
    )


@router.post("/{invoice_id}/upload")
def upload_invoice_file(
    invoice_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload file PDF hóa đơn."""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Không tìm thấy hóa đơn")
    dest_dir = os.path.join(UPLOAD_DIR, "invoices")
    os.makedirs(dest_dir, exist_ok=True)
    filename = f"invoice_{invoice_id}_{file.filename}"
    dest = os.path.join(dest_dir, filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    invoice.file_path = dest
    db.commit()
    return RedirectResponse(url=f"/invoices/{invoice_id}", status_code=302)


@router.post("/{invoice_id}/delete")
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if invoice:
        db.delete(invoice)
        db.commit()
    return RedirectResponse(url="/invoices", status_code=302)
