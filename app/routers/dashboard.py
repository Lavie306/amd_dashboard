from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
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
