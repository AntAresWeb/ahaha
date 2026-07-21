"""Сущность Отклик на вакансию."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

MIN_MATCH_SCORE = 0
MAX_MATCH_SCORE = 100


class VacancyReplyStatus(str, Enum):
    """Статус отклика на вакансию."""
    PENDING = "pending"
    READY = "ready"
    SENT = "sent"
    FAILED = "failed"
    REJECTED = "rejected"


@dataclass
class VacancyReply:
    """
    Отклик на вакансию.
    """
    vacancy_id: str
    resume_id: int
    id: int | None = None
    analysis_id: int | None = None
    cover_letter: str | None = None
    match_score: float | None = None
    status: VacancyReplyStatus = VacancyReplyStatus.PENDING
    error_message: str | None = None
    message_id: str | None = None
    retry_count: int = 0
    sent_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Валидация после создания."""
        if not self.vacancy_id:
            raise ValueError("vacancy_id обязательное поле")
        if not self.resume_id:
            raise ValueError("resume_id обязательное поле")
        if self.match_score is not None:
            # Приводим к float, если пришла строка
            try:
                score = float(self.match_score)
            except (TypeError, ValueError) as e:
                raise ValueError("match_score должен быть числом") from e
            if not (MIN_MATCH_SCORE <= score <= MAX_MATCH_SCORE):
                raise ValueError(
                    f"match_score должен быть в диапазоне "
                    f"{MIN_MATCH_SCORE}-{MAX_MATCH_SCORE}",
                )

    def mark_ready(self) -> None:
        """Отметить отклик как готовый к отправке."""
        self.status = VacancyReplyStatus.READY
        self.updated_at = datetime.now(timezone.utc)

    def mark_sent(self, message_id: str) -> None:
        """Отметить отклик как отправленный."""
        self.status = VacancyReplyStatus.SENT
        self.message_id = message_id
        self.sent_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def mark_failed(self, error: str) -> None:
        """Отметить отклик как неудачный."""
        self.error_message = error
        self.retry_count += 1
        self.status = VacancyReplyStatus.FAILED
        self.updated_at = datetime.now(timezone.utc)

    def mark_rejected(self, reason: str) -> None:
        """Отметить отклик как отклоненный."""
        self.error_message = reason
        self.status = VacancyReplyStatus.REJECTED
        self.updated_at = datetime.now(timezone.utc)
