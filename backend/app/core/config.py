from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from pathlib import Path

# Get the backend directory (where .env should be)
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    # App
    app_name: str = "Alpha Genie"
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./data/alpha_genie.db"

    # Auth
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # LLM
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    default_llm: str = "openai"

    # External APIs
    earnings_api_key: str = Field(default="", alias="EARNINGS_API_KEY")

    # File Storage
    upload_dir: str = "./data/uploads"
    max_upload_size: int = 10 * 1024 * 1024

    class Config:
        env_file = str(ENV_FILE)
        extra = "ignore"
        populate_by_name = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()