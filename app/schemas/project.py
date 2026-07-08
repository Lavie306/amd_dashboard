from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from app.models.project import ProjectStatus, ContractType


class PaymentStageBase(BaseModel):
    name: str
    amount: Decimal = Decimal("0")
    received_date: Optional[date] = None
    notes: Optional[str] = None


class PaymentStageCreate(PaymentStageBase):
    pass


class PaymentStageRead(PaymentStageBase):
    id: int
    project_id: int

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    name: str
    customer_id: int
    status: ProjectStatus = ProjectStatus.ongoing
    description: Optional[str] = None
    start_date: Optional[date] = None
    expected_delivery: Optional[date] = None
    tech_stack: Optional[str] = None
    repo_url: Optional[str] = None
    staging_url: Optional[str] = None
    production_url: Optional[str] = None
    tech_notes: Optional[str] = None
    contract_type: Optional[ContractType] = None
    contract_notes: Optional[str] = None
    total_value: Optional[Decimal] = Decimal("0")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    name: Optional[str] = None
    customer_id: Optional[int] = None
    status: Optional[ProjectStatus] = None


class ProjectRead(ProjectBase):
    id: int
    contract_file: Optional[str] = None
    payment_stages: List[PaymentStageRead] = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
