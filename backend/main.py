# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.database import Base, engine

# import models so SQLAlchemy sees them before create_all
from .models import user as _user_model  # noqa: F401
from .models import location as _location_model  # noqa: F401

from .routers import auth, weather, locations

def create_app() -> FastAPI:
    app = FastAPI(title="Weather API", version="1.0.0")

    # CORS: set your frontend origin here (edit when you add React)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # change for prod (e.g., your domain)
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def on_startup():
        # simple learning/dev path; use Alembic in prod
        Base.metadata.create_all(bind=engine)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/")
    def root():
        return {
            "message": "Weather API backend is running",
            "docs": "/docs",
            "health": "/health",
        }

    # Routers
    app.include_router(auth.router)       # /auth (register, login, me)
    app.include_router(weather.router)    # /weather (current, forecast)
    app.include_router(locations.router)  # /locations (CRUD favorites)

    return app

app = create_app()
