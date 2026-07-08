from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from app.routers import auth, dashboard, customers, projects, domains, servers, invoices, managed_it, products, ai_import

app = FastAPI(
    title="AMD Internal Management System",
    description="Hệ thống quản lý nội bộ AMD",
    version="1.0.0",
)

# Session middleware (dùng cho login session)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "fallback-secret-key"),
    max_age=86400,  # 24 giờ
)

# Static files (CSS, JS, images)
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Upload files
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include tất cả routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(customers.router)
app.include_router(projects.router)
app.include_router(domains.router)
app.include_router(servers.router)
app.include_router(invoices.router)
app.include_router(managed_it.router)
app.include_router(products.router)
app.include_router(ai_import.router)


@app.exception_handler(401)
async def unauthorized_handler(request: Request, exc):
    """Redirect về trang login khi chưa đăng nhập."""
    return RedirectResponse(url="/login", status_code=302)
