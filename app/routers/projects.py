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
from app.models.project import Project, ProjectStatus, ContractType, PaymentStage
from app.models.customer import Customer

router = APIRouter(prefix="/projects", tags=["projects"])
templates = Jinja2Templates(directory="app/templates")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")


@router.get("/", response_class=HTMLResponse)
def list_projects(
    request: Request,
    q: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Project)
    if q:
        query = query.filter(Project.name.ilike(f"%{q}%"))
    if status_filter:
        query = query.filter(Project.status == status_filter)
    projects = query.order_by(Project.created_at.desc()).all()
    statuses = [s.value for s in ProjectStatus]
    return templates.TemplateResponse(
        "projects/list.html",
        {"request": request, "current_user": current_user, "projects": projects, "q": q, "status_filter": status_filter, "statuses": statuses},
    )


@router.get("/new", response_class=HTMLResponse)
def new_project_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customers = db.query(Customer).order_by(Customer.name).all()
    statuses = [s.value for s in ProjectStatus]
    contract_types = [c.value for c in ContractType]
    return templates.TemplateResponse(
        "projects/form.html",
        {"request": request, "current_user": current_user, "project": None, "customers": customers, "statuses": statuses, "contract_types": contract_types},
    )


@router.post("/")
def create_project(
    request: Request,
    name: str = Form(...),
    customer_id: int = Form(...),
    status: str = Form(...),
    description: Optional[str] = Form(None),
    start_date: Optional[str] = Form(None),
    expected_delivery: Optional[str] = Form(None),
    tech_stack: Optional[str] = Form(None),
    repo_url: Optional[str] = Form(None),
    staging_url: Optional[str] = Form(None),
    production_url: Optional[str] = Form(None),
    tech_notes: Optional[str] = Form(None),
    contract_type: Optional[str] = Form(None),
    contract_notes: Optional[str] = Form(None),
    total_value: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = Project(
        name=name,
        customer_id=customer_id,
        status=ProjectStatus(status),
        description=description,
        start_date=date.fromisoformat(start_date) if start_date else None,
        expected_delivery=date.fromisoformat(expected_delivery) if expected_delivery else None,
        tech_stack=tech_stack,
        repo_url=repo_url,
        staging_url=staging_url,
        production_url=production_url,
        tech_notes=tech_notes,
        contract_type=ContractType(contract_type) if contract_type else None,
        contract_notes=contract_notes,
        total_value=Decimal(total_value) if total_value else Decimal("0"),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return RedirectResponse(url=f"/projects/{project.id}", status_code=302)


@router.get("/{project_id}", response_class=HTMLResponse)
def project_detail(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án")
    total_received = sum(s.amount for s in project.payment_stages if s.received_date)
    remaining = (project.total_value or 0) - total_received
    return templates.TemplateResponse(
        "projects/detail.html",
        {"request": request, "current_user": current_user, "project": project, "total_received": total_received, "remaining": remaining},
    )


@router.get("/{project_id}/edit", response_class=HTMLResponse)
def edit_project_form(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án")
    customers = db.query(Customer).order_by(Customer.name).all()
    statuses = [s.value for s in ProjectStatus]
    contract_types = [c.value for c in ContractType]
    return templates.TemplateResponse(
        "projects/form.html",
        {"request": request, "current_user": current_user, "project": project, "customers": customers, "statuses": statuses, "contract_types": contract_types},
    )


@router.post("/{project_id}/update")
def update_project(
    project_id: int,
    name: str = Form(...),
    customer_id: int = Form(...),
    status: str = Form(...),
    description: Optional[str] = Form(None),
    start_date: Optional[str] = Form(None),
    expected_delivery: Optional[str] = Form(None),
    tech_stack: Optional[str] = Form(None),
    repo_url: Optional[str] = Form(None),
    staging_url: Optional[str] = Form(None),
    production_url: Optional[str] = Form(None),
    tech_notes: Optional[str] = Form(None),
    contract_type: Optional[str] = Form(None),
    contract_notes: Optional[str] = Form(None),
    total_value: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án")
    project.name = name
    project.customer_id = customer_id
    project.status = ProjectStatus(status)
    project.description = description
    project.start_date = date.fromisoformat(start_date) if start_date else None
    project.expected_delivery = date.fromisoformat(expected_delivery) if expected_delivery else None
    project.tech_stack = tech_stack
    project.repo_url = repo_url
    project.staging_url = staging_url
    project.production_url = production_url
    project.tech_notes = tech_notes
    project.contract_type = ContractType(contract_type) if contract_type else None
    project.contract_notes = contract_notes
    project.total_value = Decimal(total_value) if total_value else Decimal("0")
    db.commit()
    return RedirectResponse(url=f"/projects/{project_id}", status_code=302)


@router.post("/{project_id}/contract")
def upload_contract(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload file hợp đồng cho dự án."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án")
    dest_dir = os.path.join(UPLOAD_DIR, "contracts")
    os.makedirs(dest_dir, exist_ok=True)
    filename = f"project_{project_id}_{file.filename}"
    dest = os.path.join(dest_dir, filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    project.contract_file = dest
    db.commit()
    return RedirectResponse(url=f"/projects/{project_id}", status_code=302)


@router.post("/{project_id}/payment")
def add_payment_stage(
    project_id: int,
    name: str = Form(...),
    amount: str = Form(...),
    received_date: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Thêm đợt thanh toán cho dự án."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án")
    stage = PaymentStage(
        project_id=project_id,
        name=name,
        amount=Decimal(amount),
        received_date=date.fromisoformat(received_date) if received_date else None,
        notes=notes,
    )
    db.add(stage)
    db.commit()
    return RedirectResponse(url=f"/projects/{project_id}", status_code=302)


@router.post("/{project_id}/payment/{stage_id}/delete")
def delete_payment_stage(
    project_id: int,
    stage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stage = db.query(PaymentStage).filter(PaymentStage.id == stage_id, PaymentStage.project_id == project_id).first()
    if stage:
        db.delete(stage)
        db.commit()
    return RedirectResponse(url=f"/projects/{project_id}", status_code=302)


@router.post("/{project_id}/delete")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        db.delete(project)
        db.commit()
    return RedirectResponse(url="/projects", status_code=302)
