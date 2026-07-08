from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class CustomerType(str, enum.Enum):
    individual = "individual"
    business = "business"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(Enum(CustomerType), nullable=False, default=CustomerType.individual)
    company_name = Column(String(255), nullable=True)
    tax_code = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    projects = relationship("Project", back_populates="customer", cascade="all, delete-orphan")
    domains = relationship("Domain", back_populates="customer", cascade="all, delete-orphan")
    servers = relationship("Server", back_populates="customer", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="customer", cascade="all, delete-orphan")
    managed_it_packages = relationship("ManagedITPackage", back_populates="customer", cascade="all, delete-orphan")
