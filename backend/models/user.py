from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

    favorites = relationship("FavoriteLocation", back_populates="owner", cascade="all, delete-orphan")
