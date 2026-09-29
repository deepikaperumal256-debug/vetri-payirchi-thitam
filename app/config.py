from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FitBuddy - AI Fitness Plan Generator"

    database_url: str = "sqlite:///./fitbuddy.db"

    # Gemini configuration
    gemini_api_key: str | None = None

    # Keep model names configurable so they can be changed in .env
    gemini_workout_model: str = "gemini-3.8-flash"
    gemini_nutrition_model: str = "gemini-3.8-flash"

    # Allows the project to run without Gemini during initial testing
    ai_demo_mode: bool = True

    # Local admin password/key
    admin_key: str = "change-me"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()