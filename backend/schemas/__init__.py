# backend/schemas/__init__.py
# Keep exports minimal and correct
from .user import UserCreate, UserOut
from .auth import Token, LoginRequest

__all__ = ["UserCreate", "UserOut", "Token", "LoginRequest"]
