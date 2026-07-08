from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from app.models.invoice import Invoice


class InvoiceBase(BaseModel):
    customer_id: int
    project_id: Optional[int] = None
    invoice_number: str
    issue_date: date
    amount: Decimal = Decimal("0")
    vat: Decimal = Decimal("10")
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(InvoiceBase):
    customer_id: Optional[int] = None
    invoice_number: Optional[str] = None
    issue_date: Optional[date] = None
    amount: Optional[Decimal] = None
    vat: Optional[Decimal] = None


class InvoiceRead(InvoiceBase):
    id: int
    total: Decimal
    file_path: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ManagedITBase(BaseModel):
    customer_id: int
    name: str
    description: Optional[str] = None
    price: Optional[Decimal] = None
    cycle: str = "monthly"
    start_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: str = "Đang hoạt động"
    notes: Optional[str] = None


class ManagedITCreate(ManagedITBase):
    pass


class ManagedITUpdate(ManagedITBase):
    customer_id: Optional[int] = None
    name: Optional[str] = None


class ManagedITRead(ManagedITBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    current_version: Optional[str] = None
    demo_url: Optional[str] = None
    repo_url: Optional[str] = None
    docs_url: Optional[str] = None
    status: str = "Đang phát triển"
    notes: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    name: Optional[str] = None


class ProductRead(ProductBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
