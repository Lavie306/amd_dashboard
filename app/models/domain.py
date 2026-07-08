from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class DomainStatus(str, enum.Enum):
    active = "Đang hoạt động"
    expired = "Hết hạn"
    transferred = "Đã chuyển"


class Domain(Base):
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    domain_name = Column(String(255), nullable=False, index=True)
    registrar = Column(String(255), nullable=True)
    registered_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True, index=True)
    auto_renew = Column(Boolean, default=False)
    status = Column(Enum(DomainStatus), nullable=False, default=DomainStatus.active)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="domains")
    project = relationship("Project", back_populates="domains")
