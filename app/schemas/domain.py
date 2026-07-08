from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from app.models.domain import DomainStatus


class DomainBase(BaseModel):
    customer_id: int
    project_id: Optional[int] = None
    domain_name: str
    registrar: Optional[str] = None
    registered_date: Optional[date] = None
    expiry_date: Optional[date] = None
    auto_renew: bool = False
    status: DomainStatus = DomainStatus.active
    notes: Optional[str] = None


class DomainCreate(DomainBase):
    pass


class DomainUpdate(DomainBase):
    customer_id: Optional[int] = None
    domain_name: Optional[str] = None


class DomainRead(DomainBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
