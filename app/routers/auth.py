from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import bcrypt
from app.database import get_db
from app.models.user import User

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))



@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Trang đăng nhập."""
    if request.session.get("user_id"):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Xử lý đăng nhập — kiểm tra username/password, tạo session."""
    user = db.query(User).filter(User.username == username, User.is_active == True).first()

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Tên đăng nhập hoặc mật khẩu không đúng"},
            status_code=400,
        )

    request.session["user_id"] = user.id
    request.session["username"] = user.username
    return RedirectResponse(url="/", status_code=302)


@router.get("/logout")
def logout(request: Request):
    """Đăng xuất — xoá session."""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)
