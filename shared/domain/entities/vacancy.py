"""Сущность Вакансия."""
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Vacancy:
    """
    Вакансия с HeadHunter.

    Используется всеми сервисами:
    - Fetcher: создает и сохраняет
    - Analyzer: читает для анализа
    - Sender: читает для отправки отклика
    - Gateway: читает для отображения
    """

    # --- Основные идентификаторы ---
    external_id: str                     # ID вакансии в HH ("133473143")
    url: str                             # "https://hh.ru/vacancy/133473143"
    alternate_url: str                   # URL для API

    # --- Название и работодатель ---
    name: str                            # "Python-разработчик (Django)"
    employer_id: str                     # "123123"
    employer_name: str                   # "Shtab"
    company_logo_url: str | None = None

    # --- Описание ---
    requirement: str                     # HTML-фрагмент требований
    responsibility: str                  # HTML-фрагмент обязанностей

    # --- Зарплата ---
    salary_from: int | None = None       # 150000
    salary_to: int | None = None         # 180000
    currency: str = "RUR"                # "RUR"
    gross: bool = True                   # True = до налогов, False = на руки

    # --- Локация ---
    city: str | None = None              # "Санкт-Петербург"
    area_id: str | None = None           # ID региона

    # --- Опыт работы ---
    experience_id: str | None = None     # "between1And3"
    experience_name: str | None = None   # "От 1 года до 3 лет"

    # --- Формат работы ---
    work_format: str = "REMOTE"          # ON_SITE, REMOTE, MIXED

    # --- Метаданные ---
    published_at: datetime               # Дата публикации
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_archived: bool = False            # Архив (вакансия закрыта)
    full_text: str | None = None         # Полный текст (подгружается позже)

    def __post_init__(self) -> None:
        """Валидация после создания."""
        if not self.external_id:
            raise ValueError("external_id не может быть пустым")
        if not self.name:
            raise ValueError("name не может быть пустым")
        if not self.employer_id:
            raise ValueError("employer_id не может быть пустым")
        if not self.url:
            raise ValueError("url не может быть пустым")
