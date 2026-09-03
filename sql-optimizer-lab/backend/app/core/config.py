from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    api_cors_origins: str = "http://localhost:3000"
    default_timeout_ms: int = 5000
    max_timeout_ms: int = 15000
    max_iterations: int = 5
    default_repeats: int = 3
    llm_provider: str = "none"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
