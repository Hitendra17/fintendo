from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    log_level: str = "INFO"

    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"

    embedding_provider: str = "qwen_local"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="FINTENDO_",
        case_sensitive=False,
    )


settings = Settings()