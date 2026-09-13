from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    log_level: str = "INFO"

    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"

    embedding_provider: str = "qwen_local"

    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="FINTENDO_",
        case_sensitive=False,
    )


settings = Settings()