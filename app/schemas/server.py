from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from app.models.server import ServerType, ServerStatus


class ServerCredentialBase(BaseModel):
    key: str
    value: str


class ServerCredentialCreate(ServerCredentialBase):
    pass


class ServerCredentialRead(ServerCredentialBase):
    id: int
    server_id: int

    class Config:
        from_attributes = True


class ServerBase(BaseModel):
    customer_id: int
    project_id: Optional[int] = None
    label: str
    type: ServerType = ServerType.vps
    provider: Optional[str] = None
    ip_address: Optional[str] = None
    os: Optional[str] = None
    purchase_date: Optional[date] = None
    expiry_date: Optional[date] = None
    monthly_cost: Optional[Decimal] = None
    status: ServerStatus = ServerStatus.active
    notes: Optional[str] = None


class ServerCreate(ServerBase):
    pass


class ServerUpdate(ServerBase):
    customer_id: Optional[int] = None
    label: Optional[str] = None


class ServerRead(ServerBase):
    id: int
    credentials: List[ServerCredentialRead] = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
