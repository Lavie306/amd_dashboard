from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.customer import Customer, CustomerType

router = APIRouter(prefix="/customers", tags=["customers"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def list_customers(
    request: Request,
    q: Optional[str] = None,
    type_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Danh sách khách hàng, có tìm kiếm và filter."""
    query = db.query(Customer)
    if q:
        query = query.filter(
            Customer.name.ilike(f"%{q}%")
            | Customer.email.ilike(f"%{q}%")
            | Customer.phone.ilike(f"%{q}%")
        )
    if type_filter in ("individual", "business"):
        query = query.filter(Customer.type == type_filter)

    customers = query.order_by(Customer.name).all()
    return templates.TemplateResponse(
        "customers/list.html",
        {"request": request, "current_user": current_user, "customers": customers, "q": q, "type_filter": type_filter},
    )


@router.get("/new", response_class=HTMLResponse)
def new_customer_form(request: Request, current_user: User = Depends(get_current_user)):
    """Form tạo khách hàng mới."""
    return templates.TemplateResponse(
        "customers/form.html",
        {"request": request, "current_user": current_user, "customer": None},
    )


@router.post("/")
def create_customer(
    request: Request,
    name: str = Form(...),
    type: str = Form(...),
    company_name: Optional[str] = Form(None),
    tax_code: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lưu khách hàng mới vào DB."""
    customer = Customer(
        name=name,
        type=CustomerType(type),
        company_name=company_name,
        tax_code=tax_code,
        email=email,
        phone=phone,
        address=address,
        notes=notes,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return RedirectResponse(url=f"/customers/{customer.id}", status_code=302)


@router.get("/{customer_id}", response_class=HTMLResponse)
def customer_detail(
    customer_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Chi tiết một khách hàng — hiện dự án, domain, hóa đơn, managed IT liên quan."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
    return templates.TemplateResponse(
        "customers/detail.html",
        {"request": request, "current_user": current_user, "customer": customer},
    )


@router.get("/{customer_id}/edit", response_class=HTMLResponse)
def edit_customer_form(
    customer_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Form chỉnh sửa khách hàng."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
    return templates.TemplateResponse(
        "customers/form.html",
        {"request": request, "current_user": current_user, "customer": customer},
    )


@router.post("/{customer_id}/update")
def update_customer(
    customer_id: int,
    request: Request,
    name: str = Form(...),
    type: str = Form(...),
    company_name: Optional[str] = Form(None),
    tax_code: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cập nhật thông tin khách hàng."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")

    customer.name = name
    customer.type = CustomerType(type)
    customer.company_name = company_name
    customer.tax_code = tax_code
    customer.email = email
    customer.phone = phone
    customer.address = address
    customer.notes = notes
    db.commit()
    return RedirectResponse(url=f"/customers/{customer_id}", status_code=302)


@router.post("/{customer_id}/delete")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Xoá khách hàng (cascade xoá luôn dự án, domain, server liên quan)."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
    db.delete(customer)
    db.commit()
    return RedirectResponse(url="/customers", status_code=302)
