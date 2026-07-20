from functools import lru_cache

from pydantic import Field, SecretStr

from shared.config.base import Settings


class RabbitMQSettings(Settings):
    """Настройки для RabbitMQ."""

    # --- Параметры подключения ---
    host: str = Field(
        default="localhost",
        alias="RABBITMQ_HOST",
        description="Хост RabbitMQ",
    )
    port: int = Field(
        default=5672,
        alias="RABBITMQ_PORT",
        description="Порт RabbitMQ",
    )
    user: str = Field(
        default="guest",
        alias="RABBITMQ_USER",
        description="Имя пользователя",
    )
    password: SecretStr = Field(
        default="guest",
        alias="RABBITMQ_PASSWORD",
        description="Пароль пользователя",
    )
    vhost: str = Field(
        default="/",
        alias="RABBITMQ_VHOST",
        description="Virtual host",
    )

    # --- Настройки очередей ---
    exchange_name: str = Field(
        default="vacancies.exchange",
        alias="RABBITMQ_EXCHANGE",
        description="Имя обменника",
    )
    queue_analyzer_pending: str = Field(
        default="analyzer.pending",
        alias="RABBITMQ_QUEUE_ANALYZER_PENDING",
        description="Очередь для анализа",
    )
    queue_sender_ready: str = Field(
        default="sender.ready",
        alias="RABBITMQ_QUEUE_SENDER_READY",
        description="Очередь для отправки",
    )
    dead_letter_queue: str = Field(
        default="dead.letter",
        alias="RABBITMQ_DEAD_LETTER_QUEUE",
        description="Очередь для ошибок",
    )

    # --- Настройки повторных попыток ---
    max_retries: int = Field(
        default=3,
        alias="RABBITMQ_MAX_RETRIES",
        description="Максимальное количество повторных попыток",
    )
    retry_interval_seconds: int = Field(
        default=60,
        alias="RABBITMQ_RETRY_INTERVAL_SECONDS",
        description="Интервал между повторными попытками",
    )

    @property
    def connection_url(self) -> str:
        """Собирает URL для подключения к RabbitMQ."""
        return (
            f"amqp://{self.user}"
            f":{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}"
            f"{self.vhost}"
        )


@lru_cache(maxsize=1)
def get_rabbitmq_settings() -> RabbitMQSettings:
    """Возвращает синглтон-экземпляр RabbitMQSettings."""
    return RabbitMQSettings()
