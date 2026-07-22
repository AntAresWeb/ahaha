"""Сущность Резюме."""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Resume:
    """
    Резюме соискателя.
    """
    profession: str
    full_text: str
    id: int | None = None
    hh_resume_id: str | None = None
    skills: list[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Валидация после создания."""
        if not self.profession:
            raise ValueError("profession не может быть пустым")
        if not self.full_text:
            raise ValueError("full_text не может быть пустым")
