# backend/crud/user.py
from sqlalchemy.orm import Session
from ..models.user import User
from ..auth.security import get_password_hash, verify_password

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, password: str, full_name: str | None = None) -> User:
    user = User(email=email, hashed_password=get_password_hash(password), full_name=full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
