from sqlalchemy import Column, Integer, String, Text, Date, Numeric, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ProjectStatus(str, enum.Enum):
    ongoing = "Đang triển khai"
    delivered = "Đã bàn giao"
    maintenance = "Bảo trì"
    paused = "Tạm dừng"
    closed = "Đã đóng"


class ContractType(str, enum.Enum):
    individual = "individual"
    legal = "legal"
    both = "both"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    status = Column(Enum(ProjectStatus), nullable=False, default=ProjectStatus.ongoing)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    expected_delivery = Column(Date, nullable=True)
    tech_stack = Column(String(500), nullable=True)
    repo_url = Column(String(500), nullable=True)
    staging_url = Column(String(500), nullable=True)
    production_url = Column(String(500), nullable=True)
    tech_notes = Column(Text, nullable=True)

    # Contract
    contract_file = Column(String(500), nullable=True)
    contract_type = Column(Enum(ContractType), nullable=True)
    contract_notes = Column(Text, nullable=True)

    # Payment
    total_value = Column(Numeric(15, 2), nullable=True, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="projects")
    payment_stages = relationship("PaymentStage", back_populates="project", cascade="all, delete-orphan")
    domains = relationship("Domain", back_populates="project")
    servers = relationship("Server", back_populates="project")
    invoices = relationship("Invoice", back_populates="project")


class PaymentStage(Base):
    __tablename__ = "payment_stages"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False, default=0)
    received_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="payment_stages")
