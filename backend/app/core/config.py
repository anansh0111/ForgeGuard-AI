from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        protected_namespaces=("settings_",),  # avoids model_ prefix warning
    )

    app_name: str = "ForgeGuard AI"
    app_version: str = "1.0.0"
    database_url: str = "postgresql://forgeguard:forgeguard_secret@localhost:5432/forgeguard_db"
    env: str = "development"
    model_path: str = "/app/ml/best_model.pkl"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
