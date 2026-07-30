from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Definición de la clase de configuración para la aplicación
class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8")

settings = Settings()  #type: ignore


