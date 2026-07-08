"""
Script khoi tao database va tao user admin mac dinh.
Chay: python init_db.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
import app.models  # Import tat ca models de SQLAlchemy nhan dien
from app.models.user import User
import bcrypt


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def init_db():
    print("[*] Dang tao bang database...")
    Base.metadata.create_all(bind=engine)
    print("[OK] Tao bang thanh cong!")

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "admin").first()
        if existing:
            print("[INFO] User admin da ton tai, bo qua.")
            return

        admin = User(
            username="admin",
            email="admin@amd.vn",
            hashed_password=hash_password("admin123"),
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print("[OK] Tao user admin thanh cong!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   [!] Hay doi mat khau sau khi dang nhap!")

    finally:
        db.close()


if __name__ == "__main__":
    init_db()
