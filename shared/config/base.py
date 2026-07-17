from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Базовый класс для всех настроек.
    Определяет общие параметры для всех под-конфигов.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Общие настройки (можно переопределить в под-классах)
    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
        description="Уровень логирования",
    )

