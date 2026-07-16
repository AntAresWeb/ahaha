from functools import lru_cache

from pydantic import Field

from src.vacancy_analizer.infrastructure.config.base import Settings


class LoggingSettings(Settings):
    """Настройки для логирования."""

    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
        description="Уровень логирования",
    )
    log_format: str = Field(
        default="text",
        alias="LOG_FORMAT",
        description="Формат логов (text или json)",
    )
    log_file: str = Field(
        default="app.log",
        alias="LOG_FILE",
        description="Файл для записи логов",
    )


@lru_cache(maxsize=1)
def get_logging_settings() -> LoggingSettings:
    """Возвращает синглтон-экземпляр LoggingSettings."""
    return LoggingSettings()
