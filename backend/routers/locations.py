# backend/routers/locations.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth.deps import get_current_user
from ..core.database import get_db
from ..crud import location as loc_crud
from ..models.user import User
from ..schemas.location import FavoriteCreate, FavoriteOut

router = APIRouter(prefix="/locations", tags=["locations"])

@router.get("/", response_model=list[FavoriteOut])
def list_favorites(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    favs = loc_crud.list_for_user(db, user.id)
    return [FavoriteOut(id=f.id, name=f.name, query=f.query) for f in favs]

@router.post("/", response_model=FavoriteOut, status_code=status.HTTP_201_CREATED)
def add_favorite(payload: FavoriteCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    fav = loc_crud.create_for_user(db, user.id, payload.name, payload.query)
    return FavoriteOut(id=fav.id, name=fav.name, query=fav.query)

@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(favorite_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ok = loc_crud.delete_for_user(db, user.id, favorite_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Favorite not found")
