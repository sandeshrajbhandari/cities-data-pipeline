from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Startup City Data Pipeline"
    database_path: Path = Path("data/cities.sqlite3")
    export_dir: Path = Path("exports")
    default_city_limit: int = 220

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
