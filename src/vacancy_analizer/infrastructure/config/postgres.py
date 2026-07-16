from functools import lru_cache

from pydantic import Field, SecretStr

from src.vacancy_analizer.infrastructure.config.base import Settings


class PostgresSettings(Settings):
    """Настройки для подключения к PostgreSQL."""

    # --- Параметры подключения ---
    postgres_db: str = Field(
        default="vacancies",
        alias="POSTGRES_DB",
        description="Имя базы данных",
    )
    postgres_user: str = Field(
        default="user",
        alias="POSTGRES_USER",
        description="Имя пользователя",
    )
    postgres_password: SecretStr = Field(
        default="pass",
        alias="POSTGRES_PASSWORD",
        description="Пароль пользователя",
    )
    postgres_host: str = Field(
        default="localhost",
        alias="POSTGRES_HOST",
        description="Хост PostgreSQL",
    )
    postgres_port: int = Field(
        default=5432,
        alias="POSTGRES_PORT",
        description="Порт PostgreSQL",
    )
    postgres_driver: str = Field(
        default="postgresql+asyncpg",
        alias="POSTGRES_DRIVER",
        description="Драйвер SQLAlchemy (например, postgresql+asyncpg или postgresql+psycopg)",
    )

    # --- Настройки пула соединений ---
    db_pool_size: int = Field(
        default=5,
        alias="POSTGRES_POOL_SIZE",
        description="Размер пула соединений",
    )
    db_max_overflow: int = Field(
        default=10,
        alias="POSTGRES_MAX_OVERFLOW",
        description="Максимальное количество переполнений",
    )
    db_pool_timeout: int = Field(
        default=30,
        alias="POSTGRES_POOL_TIMEOUT",
        description="Таймаут пула соединений в секундах",
    )
    db_echo: bool = Field(
        default=False,
        alias="POSTGRES_ECHO",
        description="Логировать SQL-запросы",
    )
    db_pool_pre_ping: bool = Field(
        default=True,
        alias="POSTGRES_POOL_PRE_PING",
        description="Проверять соединение перед использованием",
    )
    db_pool_recycle: int = Field(
        default=3600,
        alias="POSTGRES_POOL_RECYCLE",
        description="Пересоздавать соединение через N секунд",
    )

    @property
    def database_url(self) -> str:
        """
        Собирает URL для подключения из параметров.
        Использует SecretStr для безопасного получения пароля.
        """
        return (
            f"{self.postgres_driver}://{self.postgres_user}"
            f":{self.postgres_password.get_secret_value()}"
            f"@{self.postgres_host}:{self.postgres_port}"
            f"/{self.postgres_db}"
        )

    @property
    def database_url_without_password(self) -> str:
        """
        URL для логирования (без пароля).
        Полезно для вывода в консоль или логи.
        """
        return (
            f"{self.postgres_driver}://{self.postgres_user}"
            f":*****@{self.postgres_host}:{self.postgres_port}"
            f"/{self.postgres_db}"
        )


@lru_cache(maxsize=1)
def get_postgres_settings() -> PostgresSettings:
    """Возвращает синглтон-экземпляр PostgresSettings."""
    return PostgresSettings()
