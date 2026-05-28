try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:  # pragma: no cover
    from pydantic import BaseSettings


    class Settings(BaseSettings):
        database_url: str = ""
        secret_key: str = ""
        environment: str = "development"
        access_token_expire_minutes: int = 60
        cors_origins: str = ""
        upload_dir: str = "uploads"
        max_upload_size_mb: int = 20

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            extra = "ignore"

        @property
        def cors_origin_list(self) -> list[str]:
            return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
else:

    class Settings(BaseSettings):
        model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

        database_url: str = ""
        secret_key: str = ""
        environment: str = "development"
        access_token_expire_minutes: int = 60
        cors_origins: str = ""
        upload_dir: str = "uploads"
        max_upload_size_mb: int = 20

        @property
        def cors_origin_list(self) -> list[str]:
            return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()

if not settings.database_url:
    raise RuntimeError("DATABASE_URL is required. Set it in the environment or backend/.env before starting the backend.")

if not settings.secret_key:
    raise RuntimeError("SECRET_KEY is required. Set it in the environment or backend/.env before starting the backend.")
