# backend/schemas/user.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None

    # Pydantic v2: enable ORM -> Pydantic conversion
    model_config = {"from_attributes": True}
