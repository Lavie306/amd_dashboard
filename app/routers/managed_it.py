from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from datetime import date
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.managed_it import ManagedITPackage, ManagedITStatus, ManagedITCycle
from app.models.customer import Customer

router = APIRouter(prefix="/managed-it", tags=["managed_it"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def list_packages(
    request: Request,
    q: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ManagedITPackage)
    if q:
        query = query.filter(ManagedITPackage.name.ilike(f"%{q}%"))
    if status_filter:
        query = query.filter(ManagedITPackage.status == status_filter)
    packages = query.order_by(ManagedITPackage.expiry_date).all()
    statuses = [s.value for s in ManagedITStatus]
    return templates.TemplateResponse(
        "managed_it/list.html",
        {"request": request, "current_user": current_user, "packages": packages, "q": q, "status_filter": status_filter, "statuses": statuses},
    )


@router.get("/new", response_class=HTMLResponse)
def new_package_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customers = db.query(Customer).order_by(Customer.name).all()
    cycles = [c.value for c in ManagedITCycle]
    statuses = [s.value for s in ManagedITStatus]
    return templates.TemplateResponse(
        "managed_it/form.html",
        {"request": request, "current_user": current_user, "package": None, "customers": customers, "cycles": cycles, "statuses": statuses},
    )


@router.post("/")
def create_package(
    customer_id: int = Form(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: Optional[str] = Form(None),
    cycle: str = Form(...),
    start_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    status: str = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pkg = ManagedITPackage(
        customer_id=customer_id,
        name=name,
        description=description,
        price=Decimal(price) if price else None,
        cycle=ManagedITCycle(cycle),
        start_date=date.fromisoformat(start_date) if start_date else None,
        expiry_date=date.fromisoformat(expiry_date) if expiry_date else None,
        status=ManagedITStatus(status),
        notes=notes,
    )
    db.add(pkg)
    db.commit()
    db.refresh(pkg)
    return RedirectResponse(url=f"/managed-it/{pkg.id}", status_code=302)


@router.get("/{pkg_id}", response_class=HTMLResponse)
def package_detail(
    pkg_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pkg = db.query(ManagedITPackage).filter(ManagedITPackage.id == pkg_id).first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Không tìm thấy gói Managed IT")
    return templates.TemplateResponse(
        "managed_it/detail.html",
        {"request": request, "current_user": current_user, "package": pkg},
    )


@router.get("/{pkg_id}/edit", response_class=HTMLResponse)
def edit_package_form(
    pkg_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pkg = db.query(ManagedITPackage).filter(ManagedITPackage.id == pkg_id).first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Không tìm thấy gói Managed IT")
    customers = db.query(Customer).order_by(Customer.name).all()
    cycles = [c.value for c in ManagedITCycle]
    statuses = [s.value for s in ManagedITStatus]
    return templates.TemplateResponse(
        "managed_it/form.html",
        {"request": request, "current_user": current_user, "package": pkg, "customers": customers, "cycles": cycles, "statuses": statuses},
    )


@router.post("/{pkg_id}/update")
def update_package(
    pkg_id: int,
    customer_id: int = Form(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: Optional[str] = Form(None),
    cycle: str = Form(...),
    start_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    status: str = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pkg = db.query(ManagedITPackage).filter(ManagedITPackage.id == pkg_id).first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Không tìm thấy gói Managed IT")
    pkg.customer_id = customer_id
    pkg.name = name
    pkg.description = description
    pkg.price = Decimal(price) if price else None
    pkg.cycle = ManagedITCycle(cycle)
    pkg.start_date = date.fromisoformat(start_date) if start_date else None
    pkg.expiry_date = date.fromisoformat(expiry_date) if expiry_date else None
    pkg.status = ManagedITStatus(status)
    pkg.notes = notes
    db.commit()
    return RedirectResponse(url=f"/managed-it/{pkg_id}", status_code=302)


@router.post("/{pkg_id}/delete")
def delete_package(
    pkg_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pkg = db.query(ManagedITPackage).filter(ManagedITPackage.id == pkg_id).first()
    if pkg:
        db.delete(pkg)
        db.commit()
    return RedirectResponse(url="/managed-it", status_code=302)
