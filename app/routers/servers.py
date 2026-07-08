from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from datetime import date
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.server import Server, ServerStatus, ServerType, ServerCredential
from app.models.customer import Customer
from app.models.project import Project

router = APIRouter(prefix="/servers", tags=["servers"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def list_servers(
    request: Request,
    q: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Server)
    if q:
        query = query.filter(Server.label.ilike(f"%{q}%") | Server.ip_address.ilike(f"%{q}%"))
    if status_filter:
        query = query.filter(Server.status == status_filter)
    servers = query.order_by(Server.expiry_date).all()
    statuses = [s.value for s in ServerStatus]
    return templates.TemplateResponse(
        "servers/list.html",
        {"request": request, "current_user": current_user, "servers": servers, "q": q, "status_filter": status_filter, "statuses": statuses},
    )


@router.get("/new", response_class=HTMLResponse)
def new_server_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customers = db.query(Customer).order_by(Customer.name).all()
    projects = db.query(Project).order_by(Project.name).all()
    server_types = [t.value for t in ServerType]
    statuses = [s.value for s in ServerStatus]
    return templates.TemplateResponse(
        "servers/form.html",
        {"request": request, "current_user": current_user, "server": None, "customers": customers, "projects": projects, "server_types": server_types, "statuses": statuses},
    )


@router.post("/")
def create_server(
    label: str = Form(...),
    customer_id: int = Form(...),
    project_id: Optional[int] = Form(None),
    type: str = Form(...),
    provider: Optional[str] = Form(None),
    ip_address: Optional[str] = Form(None),
    os: Optional[str] = Form(None),
    purchase_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    monthly_cost: Optional[str] = Form(None),
    status: str = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    server = Server(
        label=label,
        customer_id=customer_id,
        project_id=project_id or None,
        type=ServerType(type),
        provider=provider,
        ip_address=ip_address,
        os=os,
        purchase_date=date.fromisoformat(purchase_date) if purchase_date else None,
        expiry_date=date.fromisoformat(expiry_date) if expiry_date else None,
        monthly_cost=Decimal(monthly_cost) if monthly_cost else None,
        status=ServerStatus(status),
        notes=notes,
    )
    db.add(server)
    db.commit()
    db.refresh(server)
    return RedirectResponse(url=f"/servers/{server.id}", status_code=302)


@router.get("/{server_id}", response_class=HTMLResponse)
def server_detail(
    server_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Không tìm thấy server")
    return templates.TemplateResponse(
        "servers/detail.html",
        {"request": request, "current_user": current_user, "server": server},
    )


@router.get("/{server_id}/edit", response_class=HTMLResponse)
def edit_server_form(
    server_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Không tìm thấy server")
    customers = db.query(Customer).order_by(Customer.name).all()
    projects = db.query(Project).order_by(Project.name).all()
    server_types = [t.value for t in ServerType]
    statuses = [s.value for s in ServerStatus]
    return templates.TemplateResponse(
        "servers/form.html",
        {"request": request, "current_user": current_user, "server": server, "customers": customers, "projects": projects, "server_types": server_types, "statuses": statuses},
    )


@router.post("/{server_id}/update")
def update_server(
    server_id: int,
    label: str = Form(...),
    customer_id: int = Form(...),
    project_id: Optional[int] = Form(None),
    type: str = Form(...),
    provider: Optional[str] = Form(None),
    ip_address: Optional[str] = Form(None),
    os: Optional[str] = Form(None),
    purchase_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    monthly_cost: Optional[str] = Form(None),
    status: str = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Không tìm thấy server")
    server.label = label
    server.customer_id = customer_id
    server.project_id = project_id or None
    server.type = ServerType(type)
    server.provider = provider
    server.ip_address = ip_address
    server.os = os
    server.purchase_date = date.fromisoformat(purchase_date) if purchase_date else None
    server.expiry_date = date.fromisoformat(expiry_date) if expiry_date else None
    server.monthly_cost = Decimal(monthly_cost) if monthly_cost else None
    server.status = ServerStatus(status)
    server.notes = notes
    db.commit()
    return RedirectResponse(url=f"/servers/{server_id}", status_code=302)


@router.post("/{server_id}/delete")
def delete_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    server = db.query(Server).filter(Server.id == server_id).first()
    if server:
        db.delete(server)
        db.commit()
    return RedirectResponse(url="/servers", status_code=302)


# ─── Vault (Credentials) ───────────────────────────────────────────────────────

@router.post("/{server_id}/vault")
def add_credential(
    server_id: int,
    key: str = Form(...),
    value: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Thêm credential vào Vault của server."""
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Không tìm thấy server")
    cred = ServerCredential(server_id=server_id, key=key, value=value)
    db.add(cred)
    db.commit()
    return RedirectResponse(url=f"/servers/{server_id}", status_code=302)


@router.post("/{server_id}/vault/{cred_id}/delete")
def delete_credential(
    server_id: int,
    cred_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Xoá một credential khỏi Vault."""
    cred = db.query(ServerCredential).filter(
        ServerCredential.id == cred_id,
        ServerCredential.server_id == server_id,
    ).first()
    if cred:
        db.delete(cred)
        db.commit()
    return RedirectResponse(url=f"/servers/{server_id}", status_code=302)


@router.get("/{server_id}/vault/{cred_id}/reveal")
def reveal_credential(
    server_id: int,
    cred_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """API trả về value của credential (dùng AJAX để ẩn/hiện)."""
    cred = db.query(ServerCredential).filter(
        ServerCredential.id == cred_id,
        ServerCredential.server_id == server_id,
    ).first()
    if not cred:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return JSONResponse({"value": cred.value})
