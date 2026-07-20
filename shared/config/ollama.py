from functools import lru_cache

from pydantic import Field

from shared.config.base import Settings


class OllamaSettings(Settings):
    """Настройки для Ollama."""

    # --- Параметры подключения ---
    base_url: str = Field(
        default="http://localhost:11434",
        alias="OLLAMA_BASE_URL",
        description="Базовый URL Ollama API",
    )
    model: str = Field(
        default="llama3.2:3b",
        alias="OLLAMA_MODEL",
        description="Модель для анализа",
    )
    embedding_model: str = Field(
        default="nomic-embed-text",
        alias="OLLAMA_EMBEDDING_MODEL",
        description="Модель для эмбеддингов",
    )

    # --- Параметры генерации ---
    temperature: float = Field(
        default=0.3,
        alias="OLLAMA_TEMPERATURE",
        description="Температура (креативность)",
    )
    max_tokens: int = Field(
        default=500,
        alias="OLLAMA_MAX_TOKENS",
        description="Максимальное количество токенов в ответе",
    )
    top_p: float = Field(
        default=0.9,
        alias="OLLAMA_TOP_P",
        description="Nucleus sampling параметр",
    )
    repeat_penalty: float = Field(
        default=1.1,
        alias="OLLAMA_REPEAT_PENALTY",
        description="Штраф за повторение",
    )

    # --- Настройки клиента ---
    timeout_seconds: int = Field(
        default=60,
        alias="OLLAMA_TIMEOUT_SECONDS",
        description="Таймаут запроса в секундах",
    )
    max_retries: int = Field(
        default=3,
        alias="OLLAMA_MAX_RETRIES",
        description="Максимальное количество повторных попыток",
    )

    @property
    def chat_url(self) -> str:
        return f"{self.base_url}/api/chat"

    @property
    def generate_url(self) -> str:
        return f"{self.base_url}/api/generate"

    @property
    def embeddings_url(self) -> str:
        return f"{self.base_url}/api/embeddings"


@lru_cache(maxsize=1)
def get_ollama_settings() -> OllamaSettings:
    """Возвращает синглтон-экземпляр OllamaSettings."""
    return OllamaSettings()
