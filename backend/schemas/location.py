# backend/schemas/location.py
from pydantic import BaseModel

class FavoriteCreate(BaseModel):
    name: str
    query: str

class FavoriteUpdate(BaseModel):
    name: str | None = None
    query: str | None = None

class FavoriteOut(BaseModel):
    id: int
    name: str
    query: str

    model_config = {"from_attributes": True}
