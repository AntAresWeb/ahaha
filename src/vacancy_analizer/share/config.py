from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""

    # HH.ru application params
    hh_app_name: str = Field(
        default="VacancyAnalizer/1.0 (test@example.com)",
        alias="HH_APP_NAME",
        description="Name приложения",
    )
    hh_app_id: str = Field(
        default="client_id",
        alias="HH_APP_ID",
        description="ID приложения",
    )
    hh_app_secret: str = Field(
        default="client_secret",
        alias="HH_APP_SECRET",
        description="Client Secret приложения",
    )
    hh_redirect_uri: str = Field(
        default="http://localhost:8080/auth/callback",
        alias="HH_REDIRECT_URI",
        description="URI для редиректа после авторизации",
    )

    # API endpoints
    hh_api_base_url: str = Field(
        default="https://api.hh.ru",
        alias="HH_API_BASE_URL",
        description="Базовый URL API HH.ru",
    )
    hh_oauth_base_url: str = Field(
        default="https://hh.ru",
        alias="HH_OAUTH_BASE_URL",
        description="Базовый URL OAuth HH.ru",
    )

    # Application settings
    token_file: str = Field(
        default="tokens.json",
        alias="TOKEN_FILE",
        description="Файл для хранения токенов",
    )
    auto_refresh_threshold_seconds: int = Field(
        default=300,
        alias="AUTO_REFRESH_THRESHOLD_SECONDS",
        description="За сколько секунд до истечения токена начинать обновление",
    )
    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
        description="Уровень логирования",
    )

    # HTTP Client settings
    http_timeout: int = Field(
        default=30,
        alias="HTTP_TIMEOUT",
        description="Таймаут для HTTP запросов в секундах",
    )
    max_retries: int = Field(
        default=3,
        alias="MAX_RETRIES",
        description="Максимальное количество повторных попыток",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def oauth_authorize_url(self) -> str:
        """URL для авторизации"""
        return f"{self.hh_oauth_base_url}/oauth/authorize"

    @property
    def oauth_token_url(self) -> str:
        """URL для получения токена"""
        return f"{self.hh_oauth_base_url}/oauth/token"

    @property
    def api_me_url(self) -> str:
        """URL для получения информации о пользователе"""
        return f"{self.hh_api_base_url}/me"

    @property
    def api_resumes_url(self) -> str:
        """URL для получения резюме"""
        return f"{self.hh_api_base_url}/resumes/mine"

    @property
    def api_vacancies_url(self) -> str:
        """URL для поиска вакансий"""
        return f"{self.hh_api_base_url}/vacancies"


# Глобальный объект настроек
def get_settings() -> Settings:
    return Settings()
