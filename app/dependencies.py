from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """
    FastAPI dependency: Kiểm tra session, trả về User hiện tại.
    Redirect về login nếu chưa đăng nhập.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập")

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="Tài khoản không tồn tại")

    return user


def get_current_user_optional(request: Request, db: Session = Depends(get_db)):
    """Dependency không bắt buộc — trả về None nếu chưa đăng nhập."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id, User.is_active == True).first()
