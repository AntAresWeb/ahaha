from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared.infrastructure.models.base import Base


class AnalysisORM(Base):
    """ORM-модель для таблицы анализов."""

    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Связи с другими таблицами
    vacancy_id: Mapped[int] = mapped_column(ForeignKey("vacancies.external_id"), nullable=False)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), nullable=False)

    # Результаты анализа
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    strengths: Mapped[str] = mapped_column(Text, default="")  # JSON строка
    weaknesses: Mapped[str] = mapped_column(Text, default="")  # JSON строка
    analysis_details: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON строка

    # Статус
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Метрики
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<AnalysisORM(id={self.id}, vacancy_id={self.vacancy_id}, status={self.status})>"
