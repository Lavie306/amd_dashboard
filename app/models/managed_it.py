from sqlalchemy import Column, Integer, String, Text, Date, Numeric, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ManagedITStatus(str, enum.Enum):
    active = "Đang hoạt động"
    expired = "Hết hạn"
    cancelled = "Đã huỷ"


class ManagedITCycle(str, enum.Enum):
    monthly = "Tháng"
    yearly = "Năm"


class ManagedITPackage(Base):
    __tablename__ = "managed_it_packages"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    cycle = Column(Enum(ManagedITCycle), nullable=False, default=ManagedITCycle.monthly)
    start_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True, index=True)
    status = Column(Enum(ManagedITStatus), nullable=False, default=ManagedITStatus.active)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="managed_it_packages")
