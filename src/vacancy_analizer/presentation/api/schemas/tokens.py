from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TokenResponse(BaseModel):
    """Ответ от HH.ru при получении токенов"""

    access_token: str
    refresh_token: str
    token_type: str = Field(default="bearer")
    expires_in: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "abc123...",
                "refresh_token": "def456...",
                "token_type": "bearer",
                "expires_in": 1209600,
            },
        },
    )


class TokenSet(BaseModel):
    """Сохраненный набор токенов с информацией об истечении"""

    access_token: str
    refresh_token: str
    expires_at: datetime

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def is_valid(self) -> bool:
        """Проверяет, действителен ли токен"""
        return datetime.now() < self.expires_at

    @property
    def expires_in_seconds(self) -> int:
        """Количество секунд до истечения токена"""
        delta = self.expires_at - datetime.now()
        return max(0, int(delta.total_seconds()))

    @property
    def needs_refresh(self, threshold_seconds: int = 300) -> bool:
        """Нужно ли обновить токен (если истекает скоро)"""
        return self.expires_in_seconds < threshold_seconds


class UserInfo(BaseModel):
    """Информация о пользователе HH.ru"""

    id: str
    first_name: str
    last_name: str
    middle_name: str | None = None
    email: str | None = None
    is_applicant: bool | None = None
    is_employer: bool | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "12345678",
                "first_name": "Иван",
                "last_name": "Иванов",
                "middle_name": "Петрович",
                "email": "ivan@example.com",
                "is_applicant": True,
                "is_employer": False,
            },
        },
    )

    @property
    def full_name(self) -> str:
        """Полное имя пользователя"""
        parts = [self.first_name, self.last_name]
        if self.middle_name:
            parts.insert(1, self.middle_name)
        return " ".join(parts)


class AuthURLResponse(BaseModel):
    """Ответ с URL для авторизации"""

    auth_url: str
    redirect_uri: str
    message: str = "Откройте эту ссылку в браузере и разрешите доступ"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "auth_url": "https://hh.ru/oauth/authorize?response_type=code&client_id=xxx",
                "redirect_uri": "http://localhost:8080/callback",
                "message": "Откройте эту ссылку в браузере и разрешите доступ",
            },
        },
    )


class StatusResponse(BaseModel):
    """Статус токенов"""

    status: str  # 'valid', 'expired', 'no_tokens'
    expires_at: datetime | None = None
    time_left_seconds: int | None = None
    time_left_human: str | None = None
    needs_refresh: bool = False
    message: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "valid",
                "expires_at": "2026-06-17T06:42:20",
                "time_left_seconds": 604800,
                "time_left_human": "7 days, 0:00:00",
                "needs_refresh": False,
            },
        },
    )


class ErrorResponse(BaseModel):
    """Стандартный ответ с ошибкой"""

    error: str
    detail: str
    status_code: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"error": "http_exception", "detail": "Не удалось обновить токен", "status_code": 401},
        },
    )


class VacancySearchParams(BaseModel):
    """Параметры поиска вакансий"""

    text: str = Field(default="", description="Текст поиска")
    area: int = Field(default=1, description="Регион (1 - Москва)")
    per_page: int = Field(default=10, ge=1, le=100, description="Количество на странице")
    page: int = Field(default=0, ge=0, description="Номер страницы")
    only_with_salary: bool = Field(default=False, description="Только с зарплатой")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"text": "Python developer", "area": 1, "per_page": 20, "page": 0, "only_with_salary": True},
        },
    )
