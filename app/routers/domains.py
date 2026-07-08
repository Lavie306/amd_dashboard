from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.domain import Domain, DomainStatus
from app.models.customer import Customer
from app.models.project import Project

router = APIRouter(prefix="/domains", tags=["domains"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def list_domains(
    request: Request,
    q: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Domain)
    if q:
        query = query.filter(Domain.domain_name.ilike(f"%{q}%"))
    if status_filter:
        query = query.filter(Domain.status == status_filter)
    domains = query.order_by(Domain.expiry_date).all()
    statuses = [s.value for s in DomainStatus]
    return templates.TemplateResponse(
        "domains/list.html",
        {"request": request, "current_user": current_user, "domains": domains, "q": q, "status_filter": status_filter, "statuses": statuses},
    )


@router.get("/new", response_class=HTMLResponse)
def new_domain_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customers = db.query(Customer).order_by(Customer.name).all()
    projects = db.query(Project).order_by(Project.name).all()
    statuses = [s.value for s in DomainStatus]
    return templates.TemplateResponse(
        "domains/form.html",
        {"request": request, "current_user": current_user, "domain": None, "customers": customers, "projects": projects, "statuses": statuses},
    )


@router.post("/")
def create_domain(
    name: str = Form(...),
    customer_id: int = Form(...),
    project_id: Optional[str] = Form(None),
    registrar: Optional[str] = Form(None),
    registered_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    auto_renew: bool = Form(False),
    status: str = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    proj_id = int(project_id) if project_id and project_id.strip() else None
    domain = Domain(
        domain_name=name,
        customer_id=customer_id,
        project_id=proj_id,
        registrar=registrar,
        registered_date=date.fromisoformat(registered_date) if registered_date else None,
        expiry_date=date.fromisoformat(expiry_date) if expiry_date else None,
        auto_renew=auto_renew,
        status=DomainStatus(status),
        notes=notes,
    )
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return RedirectResponse(url=f"/domains/{domain.id}", status_code=302)


@router.get("/{domain_id}", response_class=HTMLResponse)
def domain_detail(
    domain_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Không tìm thấy domain")
    return templates.TemplateResponse(
        "domains/detail.html",
        {"request": request, "current_user": current_user, "domain": domain},
    )


@router.get("/{domain_id}/edit", response_class=HTMLResponse)
def edit_domain_form(
    domain_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Không tìm thấy domain")
    customers = db.query(Customer).order_by(Customer.name).all()
    projects = db.query(Project).order_by(Project.name).all()
    statuses = [s.value for s in DomainStatus]
    return templates.TemplateResponse(
        "domains/form.html",
        {"request": request, "current_user": current_user, "domain": domain, "customers": customers, "projects": projects, "statuses": statuses},
    )


@router.post("/{domain_id}/update")
def update_domain(
    domain_id: int,
    name: str = Form(...),
    customer_id: int = Form(...),
    project_id: Optional[str] = Form(None),
    registrar: Optional[str] = Form(None),
    registered_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    auto_renew: bool = Form(False),
    status: str = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Không tìm thấy domain")
    proj_id = int(project_id) if project_id and project_id.strip() else None
    domain.domain_name = name
    domain.customer_id = customer_id
    domain.project_id = proj_id
    domain.registrar = registrar
    domain.registered_date = date.fromisoformat(registered_date) if registered_date else None
    domain.expiry_date = date.fromisoformat(expiry_date) if expiry_date else None
    domain.auto_renew = auto_renew
    domain.status = DomainStatus(status)
    domain.notes = notes
    db.commit()
    return RedirectResponse(url=f"/domains/{domain_id}", status_code=302)


@router.post("/{domain_id}/delete")
def delete_domain(
    domain_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if domain:
        db.delete(domain)
        db.commit()
    return RedirectResponse(url="/domains", status_code=302)
