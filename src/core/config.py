from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str
    db_url: str
    db_url_sync: str
    rabbitmq_url: str
    redis_url: str

    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_secure: bool

    smtp_from: EmailStr
    smtp_port: int
    smtp_host: str
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_starttls: bool = True
    smtp_login: bool = True

    production_timezone: str = "Europe/Moscow"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
