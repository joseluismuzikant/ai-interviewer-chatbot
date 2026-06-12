from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "AI Interviewer Chatbot API"
    app_env: str = "development"
    app_debug: bool = True

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_storage_bucket: str = "interview-documents"

    llm_provider: str = "mock"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    google_api_key: str = ""
    google_model: str = "gemini-2.0-flash"

    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"


@lru_cache
def get_settings() -> Settings:
    return Settings()
