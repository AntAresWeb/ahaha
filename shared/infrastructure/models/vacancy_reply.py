from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared.infrastructure.models.base import Base


class VacancyReplyORM(Base):
    """ORM-модель для таблицы откликов на вакансии."""

    __tablename__ = "vacancy_replies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Связи с другими таблицами
    vacancy_id: Mapped[int] = mapped_column(ForeignKey("vacancies.external_id"), nullable=False)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), nullable=False)
    analysis_id: Mapped[int | None] = mapped_column(ForeignKey("analyses.id"), nullable=True)

    # Содержание отклика
    cover_letter: Mapped[str | None] = mapped_column(Text, nullable=True)
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Статус
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Внешние идентификаторы
    message_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Метрики
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<VacancyReplyORM(id={self.id}, vacancy_id={self.vacancy_id}, status={self.status})>"
