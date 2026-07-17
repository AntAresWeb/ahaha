from functools import lru_cache

from pydantic import Field

from shared.config.base import Settings


class HHAPISettings(Settings):
    """Настройки для работы с API HH.ru."""

    # OAuth параметры
    app_name: str = Field(
        default="VacancyAnalizer/1.0 (test@example.com)",
        alias="HH_APP_NAME",
        description="Имя приложения для HH.ru",
    )
    app_id: str = Field(
        default="client_id",
        alias="HH_APP_ID",
        description="Client ID для OAuth",
    )
    app_secret: str = Field(
        default="client_secret",
        alias="HH_APP_SECRET",
        description="Client Secret для OAuth",
    )
    redirect_uri: str = Field(
        default="http://localhost:8080/auth/callback",
        alias="HH_REDIRECT_URI",
        description="URI для редиректа после OAuth",
    )

    # API endpoints
    api_base_url: str = Field(
        default="https://api.hh.ru",
        alias="HH_API_BASE_URL",
        description="Базовый URL API HH.ru",
    )
    oauth_base_url: str = Field(
        default="https://hh.ru",
        alias="HH_OAUTH_BASE_URL",
        description="Базовый URL OAuth HH.ru",
    )

    # HTTP Client настройки (можно вынести в общий конфиг)
    http_timeout: int = Field(
        default=30,
        alias="HH_HTTP_TIMEOUT",
        description="Таймаут для HTTP запросов в секундах",
    )
    max_retries: int = Field(
        default=3,
        alias="HH_MAX_RETRIES",
        description="Максимальное количество повторных попыток",
    )

    # Дополнительные параметры
    token_file: str = Field(
        default="tokens.json",
        alias="HH_TOKEN_FILE",
        description="Файл для хранения токенов OAuth",
    )
    auto_refresh_threshold_seconds: int = Field(
        default=300,
        alias="HH_AUTO_REFRESH_THRESHOLD_SECONDS",
        description="За сколько секунд до истечения токена начинать обновление",
    )

    @property
    def oauth_authorize_url(self) -> str:
        """URL для авторизации"""
        return f"{self.oauth_base_url}/oauth/authorize"

    @property
    def oauth_token_url(self) -> str:
        """URL для получения токена"""
        return f"{self.oauth_base_url}/oauth/token"

    @property
    def api_vacancies_url(self) -> str:
        """URL для поиска вакансий"""
        return f"{self.api_base_url}/vacancies"

@lru_cache(maxsize=1)
def get_hh_api_settings() -> HHAPISettings:
    """Возвращает синглтон-экземпляр HHAPISettings."""
    return HHAPISettings()

