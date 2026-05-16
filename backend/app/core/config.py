try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:  # pragma: no cover
    from pydantic import BaseSettings


    class Settings(BaseSettings):
        database_url: str
        secret_key: str
        environment: str = "development"
        access_token_expire_minutes: int = 60
        cors_origins: str = ""

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"

        @property
        def cors_origin_list(self) -> list[str]:
            return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
else:

    class Settings(BaseSettings):
        model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

        database_url: str
        secret_key: str
        environment: str = "development"
        access_token_expire_minutes: int = 60
        cors_origins: str = ""

        @property
        def cors_origin_list(self) -> list[str]:
            return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
