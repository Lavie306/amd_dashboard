from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.customer import Customer
from app.models.project import Project
from app.models.domain import Domain
from app.models.server import Server
from app.services.expiry_service import get_expiry_alerts, get_quick_stats

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trang Dashboard chính — hiển thị cảnh báo hết hạn và thống kê."""
    alerts = get_expiry_alerts(db, days=30)
    stats = get_quick_stats(db)

    return templates.TemplateResponse(
        "dashboard/index.html",
        {
            "request": request,
            "current_user": current_user,
            "alerts": alerts,
            "stats": stats,
        },
    )


@router.get("/api/alerts")
def api_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """API trả về danh sách cảnh báo hết hạn để hiển thị ở Dropdown header."""
    alerts = get_expiry_alerts(db, days=30)
    today = alerts["today"]
    return {
        "total": alerts["total"],
        "domains": [
            {
                "id": d.id,
                "name": d.domain_name,
                "days_left": (d.expiry_date - today).days if d.expiry_date else None,
            } for d in alerts["domains"]
        ],
        "servers": [
            {
                "id": s.id,
                "name": s.label,
                "days_left": (s.expiry_date - today).days if s.expiry_date else None,
            } for s in alerts["servers"]
        ],
        "managed_it": [
            {
                "id": m.id,
                "name": m.name,
                "days_left": (m.expiry_date - today).days if m.expiry_date else None,
            } for m in alerts["managed_it"]
        ]
    }


@router.get("/api/search/suggestions")
def search_suggestions(
    q: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """API trả về gợi ý tìm kiếm tức thời cho khách hàng, dự án, domain, server."""
    if not q or len(q.strip()) < 2:
        return {"results": []}
    
    q_clean = q.strip()
    results = []
    
    # 1. Khách hàng
    customers = db.query(Customer).filter(
        (Customer.name.ilike(f"%{q_clean}%")) |
        (Customer.email.ilike(f"%{q_clean}%")) |
        (Customer.phone.ilike(f"%{q_clean}%"))
    ).limit(3).all()
    for c in customers:
        results.append({
            "title": c.name,
            "subtitle": f"Khách hàng • {c.email or c.phone or ''}",
            "url": f"/customers/{c.id}",
            "type": "customer"
        })
        
    # 2. Dự án
    projects = db.query(Project).filter(
        Project.name.ilike(f"%{q_clean}%")
    ).limit(3).all()
    for p in projects:
        status_val = p.status.value if hasattr(p.status, "value") else str(p.status)
        results.append({
            "title": p.name,
            "subtitle": f"Dự án • Trạng thái: {status_val}",
            "url": f"/projects/{p.id}",
            "type": "project"
        })
        
    # 3. Domain
    domains = db.query(Domain).filter(
        Domain.domain_name.ilike(f"%{q_clean}%")
    ).limit(3).all()
    for d in domains:
        results.append({
            "title": d.domain_name,
            "subtitle": f"Domain • Nhà đăng ký: {d.registrar or ''}",
            "url": f"/domains/{d.id}",
            "type": "domain"
        })
        
    # 4. Server
    servers = db.query(Server).filter(
        (Server.label.ilike(f"%{q_clean}%")) |
        (Server.ip_address.ilike(f"%{q_clean}%"))
    ).limit(3).all()
    for s in servers:
        results.append({
            "title": s.label,
            "subtitle": f"Server • IP: {s.ip_address or ''}",
            "url": f"/servers/{s.id}",
            "type": "server"
        })
        
    return {"results": results[:8]}
