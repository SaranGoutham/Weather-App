# backend/crud/location.py
from sqlalchemy.orm import Session
from ..models.location import FavoriteLocation

def list_for_user(db: Session, user_id: int):
    return db.query(FavoriteLocation).filter(FavoriteLocation.owner_id == user_id).all()

def create_for_user(db: Session, user_id: int, name: str, query: str):
    fav = FavoriteLocation(name=name, query=query, owner_id=user_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav

def update_for_user(db: Session, user_id: int, favorite_id: int, *, name: str | None = None, query: str | None = None):
    fav = db.query(FavoriteLocation).filter(
        FavoriteLocation.owner_id == user_id, FavoriteLocation.id == favorite_id
    ).first()
    if not fav:
        return None
    if name is not None:
        fav.name = name
    if query is not None:
        fav.query = query
    db.commit()
    db.refresh(fav)
    return fav

def delete_for_user(db: Session, user_id: int, favorite_id: int) -> bool:
    fav = db.query(FavoriteLocation).filter(
        FavoriteLocation.owner_id == user_id, FavoriteLocation.id == favorite_id
    ).first()
    if not fav:
        return False
    db.delete(fav)
    db.commit()
    return True
