"""Сущность Отклик на вакансию."""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from shared.domain.base.status_entity import StatusEntity

# Константы для валидации
MIN_MATCH_SCORE = 0
MAX_MATCH_SCORE = 100


class VacancyReplyStatus(str, Enum):
    """Статус отклика на вакансию."""
    PENDING = "pending"      # Ожидает анализа
    READY = "ready"          # Готов к отправке
    SENT = "sent"            # Отправлен
    FAILED = "failed"        # Ошибка отправки
    REJECTED = "rejected"    # Отклонен (не подошел)


@dataclass
class VacancyReply(StatusEntity[VacancyReplyStatus]):
    """
    Отклик на вакансию.

    Используется:
    - Analyzer: создает после успешного анализа
    - Sender: отправляет в HH
    - Gateway: отображает статус откликов
    """

    vacancy_id: int                     # Связь с вакансией
    resume_id: int                      # Связь с резюме
    analysis_id: int | None = None      # Связь с анализом

    # Содержание отклика
    cover_letter: str | None = None     # Текст отклика (сгенерированный)
    match_score: float | None = None    # Оценка на момент создания

    # Статус (переопределяем с дефолтным значением)
    status: VacancyReplyStatus = VacancyReplyStatus.PENDING

    # Внешние идентификаторы
    message_id: str | None = None       # ID отклика в HH

    # Метрики
    sent_at: datetime | None = None

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

    def mark_ready(self) -> None:
        """Отметить отклик как готовый к отправке."""
        self.mark_status(VacancyReplyStatus.READY)

    def mark_sent(self, message_id: str) -> None:
        """Отметить отклик как отправленный."""
        self.status = VacancyReplyStatus.SENT
        self.message_id = message_id
        self.sent_at = datetime.now(timezone.utc)
        self._update_timestamp()

    def mark_failed(self, error: str) -> None:
        """Отметить отклик как неудачный."""
        self.mark_error(error, VacancyReplyStatus.FAILED)

    def mark_rejected(self, reason: str) -> None:
        """Отметить отклик как отклоненный."""
        self.mark_error(reason, VacancyReplyStatus.REJECTED)
