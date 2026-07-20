"""Сущность Анализ соответствия."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from shared.domain.base.status_entity import StatusEntity

# Константы для валидации
MIN_MATCH_SCORE = 0
MAX_MATCH_SCORE = 100


class AnalysisStatus(str, Enum):
    """Статус анализа вакансии."""
    PENDING = "pending"          # Ожидает анализа
    IN_PROGRESS = "in_progress"  # В процессе
    COMPLETED = "completed"      # Анализ завершен
    FAILED = "failed"            # Ошибка анализа


@dataclass
class Analysis(StatusEntity[AnalysisStatus]):
    """
    Результат анализа соответствия резюме и вакансии.

    Используется:
    - Analyzer: создает и обновляет
    - Sender: проверяет статус перед отправкой
    - Gateway: отображает результаты
    """

    vacancy_id: int                     # Связь с вакансией
    resume_id: int                      # Связь с резюме

    # Результаты анализа
    match_score: float | None = None    # Оценка соответствия (0-100)
    strengths: list[str] = field(default_factory=list)   # Сильные стороны
    weaknesses: list[str] = field(default_factory=list)  # Слабые стороны
    analysis_details: str | None = None # Детальный анализ (JSON строка)

    # Статус (переопределяем с дефолтным значением)
    status: AnalysisStatus = AnalysisStatus.PENDING

    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        """Валидация после создания."""
        if self.vacancy_id <= 0:
            raise ValueError("vacancy_id должен быть положительным")
        if self.resume_id <= 0:
            raise ValueError("resume_id должен быть положительным")
        if self.match_score is not None and not (MIN_MATCH_SCORE <= self.match_score <= MAX_MATCH_SCORE):
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
        self._update_timestamp()

    def mark_failed(self, error: str) -> None:
        """Отметить анализ как неудачный."""
        self.mark_error(error, AnalysisStatus.FAILED)
        self.completed_at = datetime.now(timezone.utc)

    def mark_in_progress(self) -> None:
        """Отметить анализ как выполняющийся."""
        self.mark_status(AnalysisStatus.IN_PROGRESS)
