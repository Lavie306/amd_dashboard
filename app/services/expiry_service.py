from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.models.domain import Domain, DomainStatus
from app.models.server import Server, ServerStatus
from app.models.managed_it import ManagedITPackage, ManagedITStatus
from app.models.customer import Customer
from app.models.project import Project
from app.models.invoice import Invoice


def get_expiry_alerts(db: Session, days: int = 30) -> dict:
    """
    Lấy tất cả items sắp hết hạn trong N ngày tới.
    Trả về dict phân loại theo: domains, servers, managed_it.
    """
    today = date.today()
    deadline = today + timedelta(days=days)

    expiring_domains = (
        db.query(Domain)
        .filter(
            Domain.expiry_date.isnot(None),
            Domain.expiry_date >= today,
            Domain.expiry_date <= deadline,
            Domain.status == DomainStatus.active,
        )
        .order_by(Domain.expiry_date)
        .all()
    )

    expiring_servers = (
        db.query(Server)
        .filter(
            Server.expiry_date.isnot(None),
            Server.expiry_date >= today,
            Server.expiry_date <= deadline,
            Server.status == ServerStatus.active,
        )
        .order_by(Server.expiry_date)
        .all()
    )

    expiring_managed_it = (
        db.query(ManagedITPackage)
        .filter(
            ManagedITPackage.expiry_date.isnot(None),
            ManagedITPackage.expiry_date >= today,
            ManagedITPackage.expiry_date <= deadline,
            ManagedITPackage.status == ManagedITStatus.active,
        )
        .order_by(ManagedITPackage.expiry_date)
        .all()
    )

    return {
        "domains": expiring_domains,
        "servers": expiring_servers,
        "managed_it": expiring_managed_it,
        "total": len(expiring_domains) + len(expiring_servers) + len(expiring_managed_it),
        "today": today,
    }


def get_quick_stats(db: Session) -> dict:
    """Thống kê nhanh cho dashboard."""
    total_customers = db.query(Customer).count()
    active_projects = db.query(Project).filter(
        Project.status.in_(["Đang triển khai", "Bảo trì"])
    ).count()
    total_domains = db.query(Domain).filter(Domain.status == DomainStatus.active).count()
    invoices_without_file = db.query(Invoice).filter(Invoice.file_path.is_(None)).count()

    return {
        "total_customers": total_customers,
        "active_projects": active_projects,
        "total_domains": total_domains,
        "invoices_without_file": invoices_without_file,
    }


def days_until_expiry(expiry_date: date) -> int:
    """Tính số ngày còn lại đến ngày hết hạn."""
    if not expiry_date:
        return None
    return (expiry_date - date.today()).days
