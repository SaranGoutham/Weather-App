# backend/routers/locations.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth.deps import get_current_user
from ..core.database import get_db
from ..crud import location as loc_crud
from ..models.user import User
from ..schemas.location import FavoriteCreate, FavoriteOut, FavoriteUpdate

router = APIRouter(prefix="/locations", tags=["locations"])

@router.get("/", response_model=list[FavoriteOut])
def list_favorites(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    favs = loc_crud.list_for_user(db, user.id)
    return [FavoriteOut.model_validate(f) for f in favs]

@router.post("/", response_model=FavoriteOut, status_code=status.HTTP_201_CREATED)
def add_favorite(payload: FavoriteCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    fav = loc_crud.create_for_user(db, user.id, payload.name, payload.query)
    return FavoriteOut.model_validate(fav)

@router.patch("/{favorite_id}", response_model=FavoriteOut)
def update_favorite(
    favorite_id: int,
    payload: FavoriteUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    fav = loc_crud.update_for_user(db, user.id, favorite_id, name=payload.name, query=payload.query)
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return FavoriteOut.model_validate(fav)

@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(favorite_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ok = loc_crud.delete_for_user(db, user.id, favorite_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Favorite not found")
