import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Weather API")
    APP_ENV: str = os.getenv("APP_ENV", "dev")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    ALGORITHM: str = "HS256"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        # fallback for learning: local SQLite file
        "sqlite:///./weather.db"
    )

    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    OPENWEATHER_BASE_URL: str = os.getenv("OPENWEATHER_BASE_URL", "https://api.openweathermap.org/data/2.5")
    DEFAULT_UNITS: str = os.getenv("DEFAULT_UNITS", "metric")
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    TRUST_PROXY: bool = os.getenv("TRUST_PROXY", "false").lower() == "true"

settings = Settings()
