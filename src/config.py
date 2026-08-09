from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


# Definición de la clase de configuración para la aplicación
class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    SECRET_KEY: SecretStr
    RESEND_API_KEY: SecretStr
    R2_ACCOUNT_ID: str
    R2_ENDPOINT: str
    R2_ACCESS_KEY_ID: str
    R2_SECRET_ACCESS_KEY: SecretStr
    R2_PUBLIC_DOMAIN: str
    R2_BUCKET_AVATAR: str
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()  # type: ignore
