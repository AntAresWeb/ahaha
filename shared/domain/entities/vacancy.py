"""Сущность Вакансия."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class VacancyStatus(str, Enum):
    NEW = "new"
    FILTERED = "filtered"
    ARCHIVED = "archived"


@dataclass
class Vacancy:
    """
    Вакансия с HeadHunter.
    """
    external_id: str
    url: str
    name: str
    employer_id: str
    employer_name: str
    requirement: str
    responsibility: str
    published_at: datetime
    salary_from: int | None = None
    salary_to: int | None = None
    city: str | None = None
    experience_name: str | None = None
    work_format: str = "REMOTE"
    full_text: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    status: VacancyStatus = VacancyStatus.NEW


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
