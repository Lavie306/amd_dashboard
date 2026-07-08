from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.customer import CustomerType


class CustomerBase(BaseModel):
    name: str
    type: CustomerType = CustomerType.individual
    company_name: Optional[str] = None
    tax_code: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    name: Optional[str] = None
    type: Optional[CustomerType] = None


class CustomerRead(CustomerBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
