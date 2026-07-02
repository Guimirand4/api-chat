from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configurações da aplicação carregadas via .env"""

    # App
    app_name: str = "ChatBot API"
    app_env: str = "development"
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./app.db"

    # JWT
    secret_key: str = "change-this-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""

    # Gemini AI
    gemini_api_key: str = ""

    # CORS
    frontend_url: str = "http://localhost:3000"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache
def get_settings() -> Settings:
    """Retorna instância cacheada das configurações."""
    return Settings()
