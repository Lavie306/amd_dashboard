# Import tất cả models để SQLAlchemy nhận diện khi tạo bảng
from app.models.user import User
from app.models.customer import Customer
from app.models.project import Project, PaymentStage
from app.models.domain import Domain
from app.models.server import Server, ServerCredential
from app.models.managed_it import ManagedITPackage
from app.models.invoice import Invoice
from app.models.product import Product

__all__ = [
    "User",
    "Customer",
    "Project",
    "PaymentStage",
    "Domain",
    "Server",
    "ServerCredential",
    "ManagedITPackage",
    "Invoice",
    "Product",
]
