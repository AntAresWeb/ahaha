"""Сущность Резюме."""
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Resume:
    """
    Резюме соискателя.

    Используется:
    - Analyzer: для анализа соответствия вакансии
    - Gateway: для отображения и управления
    - Fetcher: для фильтрации вакансий
    """

    id: int | None = None
    hh_resume_id: str | None = None      # ID резюме в HH (если есть)
    profession: str                      # Профессия (для фильтрации)
    skills: list[str] = field(default_factory=list)  # Навыки списком
    full_text: str                       # Полный текст резюме
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True               # Активно ли резюме

    def __post_init__(self) -> None:
        """Валидация после создания."""
        if not self.profession:
            raise ValueError("profession не может быть пустым")
        if not self.full_text:
            raise ValueError("full_text не может быть пустым")
