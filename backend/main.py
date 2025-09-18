from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .core.config import settings
from .core.database import engine, Base
from .routers import weather, auth as auth_router, locations

def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)

    # CORS (adjust for your frontend origin)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # for learning; restrict in prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # create tables on startup (simple learning flow; use Alembic in prod)
    @app.on_event("startup")
    def on_startup():
        Base.metadata.create_all(bind=engine)
        
    @app.get("/")
    def root():
        return {"message": "Weather API backend is running!"}
    

    @app.get("/health")
    def health():
        with engine.connect() as conn:
            try:
                conn.execute(text("SELECT 1"))
                db_ok = True
            except Exception:
                db_ok = False
        return {"status": "ok", "db": db_ok, "env": settings.APP_ENV}

    app.include_router(auth_router.router)
    app.include_router(weather.router)
    app.include_router(locations.router)

    return app

app = create_app()
