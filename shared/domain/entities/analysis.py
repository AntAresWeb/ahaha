"""Сущность Анализ соответствия."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

MIN_MATCH_SCORE = 0
MAX_MATCH_SCORE = 100


class AnalysisStatus(str, Enum):
    """Статус анализа вакансии."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Analysis:
    """
    Результат анализа соответствия резюме и вакансии.
    """
    vacancy_id: str
    resume_id: int
    id: int | None = None
    match_score: float | None = None
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    analysis_details: str | None = None
    status: AnalysisStatus = AnalysisStatus.PENDING
    error_message: str | None = None
    retry_count: int = 0
    completed_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Валидация после создания."""
        if self.vacancy_id <= 0:
            raise ValueError("vacancy_id должен быть положительным")
        if self.resume_id <= 0:
            raise ValueError("resume_id должен быть положительным")
        if self.match_score is not None:
            try:
                score = float(self.match_score)
            except (TypeError, ValueError) as e:
                raise ValueError("match_score должен быть числом") from e
            if not (MIN_MATCH_SCORE <= score <= MAX_MATCH_SCORE):
                raise ValueError(
                    f"match_score должен быть в диапазоне "
                    f"{MIN_MATCH_SCORE}-{MAX_MATCH_SCORE}",
                )

    def mark_completed(self, score: float, strengths: list[str], weaknesses: list[str]) -> None:
        """Отметить анализ как завершенный."""
        if not (MIN_MATCH_SCORE <= score <= MAX_MATCH_SCORE):
            raise ValueError(f"score должен быть в диапазоне {MIN_MATCH_SCORE}-{MAX_MATCH_SCORE}")

        self.match_score = score
        self.strengths = strengths
        self.weaknesses = weaknesses
        self.status = AnalysisStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def mark_failed(self, error: str) -> None:
        """Отметить анализ как неудачный."""
        self.error_message = error
        self.retry_count += 1
        self.status = AnalysisStatus.FAILED
        self.updated_at = datetime.now(timezone.utc)

    def mark_in_progress(self) -> None:
        """Отметить анализ как выполняющийся."""
        self.status = AnalysisStatus.IN_PROGRESS
        self.updated_at = datetime.now(timezone.utc)
