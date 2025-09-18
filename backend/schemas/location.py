from pydantic import BaseModel

class FavoriteCreate(BaseModel):
    name: str
    query: str

class FavoriteOut(BaseModel):
    id: int
    name: str
    query: str
