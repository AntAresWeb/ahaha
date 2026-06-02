from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Константы URL (вынесены в одно место) ---
BASE_API_URL = "https://api.hh.ru"
OAUTH_TOKEN_URL = "https://hh.ru/oauth/token"

class HHAppSettings(BaseSettings):
    """
    Настройки для API-клиента HeadHunter.
    Загружаются из переменных окружения или .env файла.
    """
    # Обязательные настройки
    client_id: str
    client_secret: str

    # Необязательные настройки с дефолтными значениями
    base_api_url: str = BASE_API_URL
    oauth_token_url: str = OAUTH_TOKEN_URL
    timeout: float = 30.0

    # Настройки для pydantic-settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
