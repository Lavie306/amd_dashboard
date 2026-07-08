from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class ProductStatus(str, enum.Enum):
    development = "Đang phát triển"
    launched = "Đã ra mắt"
    discontinued = "Ngừng phát triển"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    current_version = Column(String(50), nullable=True)
    demo_url = Column(String(500), nullable=True)
    repo_url = Column(String(500), nullable=True)
    docs_url = Column(String(500), nullable=True)
    status = Column(Enum(ProductStatus), nullable=False, default=ProductStatus.development)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
