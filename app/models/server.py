from sqlalchemy import Column, Integer, String, Text, Date, Numeric, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ServerType(str, enum.Enum):
    vps = "VPS"
    shared = "Shared Hosting"
    dedicated = "Dedicated"
    cloud = "Cloud"


class ServerStatus(str, enum.Enum):
    active = "Đang hoạt động"
    expired = "Hết hạn"
    cancelled = "Đã huỷ"


class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    label = Column(String(255), nullable=False, index=True)
    type = Column(Enum(ServerType), nullable=False, default=ServerType.vps)
    provider = Column(String(255), nullable=True)
    ip_address = Column(String(50), nullable=True)
    os = Column(String(100), nullable=True)
    purchase_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True, index=True)
    monthly_cost = Column(Numeric(10, 2), nullable=True)
    status = Column(Enum(ServerStatus), nullable=False, default=ServerStatus.active)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="servers")
    project = relationship("Project", back_populates="servers")
    credentials = relationship("ServerCredential", back_populates="server", cascade="all, delete-orphan")


class ServerCredential(Base):
    """Vault — lưu thông tin truy cập nhạy cảm dạng key-value."""
    __tablename__ = "server_credentials"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)
    key = Column(String(255), nullable=False)
    # Lưu ý: trong production nên mã hoá value này (Fernet / AES)
    value = Column(Text, nullable=False)

    # Relationships
    server = relationship("Server", back_populates="credentials")
