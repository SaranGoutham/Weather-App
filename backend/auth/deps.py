# backend/auth/deps.py (only change is moving the import inside the function)
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt

from ..core.config import settings
from ..core.database import get_db

bearer_scheme = HTTPBearer(auto_error=False)
ALGORITHM = "HS256"

def get_current_user_email(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        return email
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def get_current_user(
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user_email),
):
    from ..crud.user import get_user_by_email  # ← lazy import avoids cycles
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
