from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Monster Dojo API"
    app_version: str = "1.0.0"
    app_env: str = "development"
    app_debug: bool = False
    app_docs_enabled: bool = True

    api_v1_prefix: str = "/api/v1"

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "MonsterDojo"
    db_user: str = "postgres"
    db_password: str = "change_me"

    secret_key: str = "change_me_super_secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    jwt_issuer: str = "monsterdojo-api"
    jwt_audience: str = "monsterdojo-client"

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    trusted_hosts: str = "localhost,127.0.0.1"
    security_headers_enabled: bool = True

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_use_tls: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @computed_field
    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @computed_field
    @property
    def trusted_hosts_list(self) -> list[str]:
        return [host.strip() for host in self.trusted_hosts.split(",") if host.strip()]

    @computed_field
    @property
    def docs_url(self) -> str | None:
        return "/docs" if self.app_docs_enabled else None

    @computed_field
    @property
    def redoc_url(self) -> str | None:
        return "/redoc" if self.app_docs_enabled else None

    @computed_field
    @property
    def openapi_url(self) -> str | None:
        return f"{self.api_v1_prefix}/openapi.json" if self.app_docs_enabled else None


@lru_cache
def get_settings() -> Settings:
    return Settings()