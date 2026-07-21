"""ORM-модель для таблицы вакансий."""
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared.infrastructure.models.base import Base


class VacancyORM(Base):
    """ORM-модель вакансии для PostgreSQL."""

    __tablename__ = "vacancies"

    # --- Основные идентификаторы ---
    external_id: Mapped[str] = mapped_column(String, primary_key=True)
    url: Mapped[str] = mapped_column(String, nullable=False)

    # --- Название и работодатель ---
    name: Mapped[str] = mapped_column(String, nullable=False)
    employer_id: Mapped[str] = mapped_column(String, nullable=False)
    employer_name: Mapped[str] = mapped_column(String, nullable=False)

    # --- Описание ---
    requirement: Mapped[str] = mapped_column(Text, default="")
    responsibility: Mapped[str] = mapped_column(Text, default="")

    # --- Зарплата ---
    salary_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_to: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # --- Локация ---
    city: Mapped[str | None] = mapped_column(String, nullable=True)

    # --- Опыт работы ---
    experience_name: Mapped[str | None] = mapped_column(String, nullable=True)

    # --- Формат работы ---
    work_format: Mapped[str] = mapped_column(String, default="REMOTE")

    # --- Метаданные ---
    published_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    full_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<VacancyORM(external_id={self.external_id}, name={self.name})>"
