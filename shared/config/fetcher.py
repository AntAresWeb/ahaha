from functools import lru_cache

from pydantic import Field

from shared.config.base import Settings


class FetcherSettings(Settings):
    """Настройки для Fetcher сервиса."""

    # --- Параметры парсинга ---
    parse_interval_minutes: int = Field(
        default=60,
        alias="FETCHER_PARSE_INTERVAL_MINUTES",
        description="Интервал парсинга в минутах",
    )
    max_vacancies_per_request: int = Field(
        default=100,
        alias="FETCHER_MAX_VACANCIES_PER_REQUEST",
        description="Максимальное количество вакансий за запрос",
    )
    min_match_score: float = Field(
        default=0.75,
        alias="FETCHER_MIN_MATCH_SCORE",
        description="Минимальный порог соответствия для анализа",
    )
    filter_by_experience: bool = Field(
        default=True,
        alias="FETCHER_FILTER_BY_EXPERIENCE",
        description="Фильтровать по опыту",
    )
    filter_by_city: bool = Field(
        default=True,
        alias="FETCHER_FILTER_BY_CITY",
        description="Фильтровать по городу",
    )

    # --- Ключевые слова для фильтрации ---
    required_skills: list[str] = Field(
        default=[],
        alias="FETCHER_REQUIRED_SKILLS",
        description="Обязательные навыки",
    )
    excluded_companies: list[str] = Field(
        default=[],
        alias="FETCHER_EXCLUDED_COMPANIES",
        description="Компании, которые нужно исключить",
    )


@lru_cache(maxsize=1)
def get_fetcher_settings() -> FetcherSettings:
    """Возвращает синглтон-экземпляр FetcherSettings."""
    return FetcherSettings()
