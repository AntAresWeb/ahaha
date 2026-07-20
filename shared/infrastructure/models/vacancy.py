from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.infrastructure.models.base import Base


class VacancyORM(Base):
    __tablename__ = "vacancies"

    external_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    employer_name: Mapped[str] = mapped_column(String, nullable=False)
    requirement: Mapped[str] = mapped_column(String, default="")
    responsibility: Mapped[str] = mapped_column(String, default="")
    published_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    url: Mapped[str] = mapped_column(String, default="")
    alternate_url: Mapped[str] = mapped_column(String, default="")

    # Зарплата
    salary_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_to: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currency: Mapped[str] = mapped_column(String, default="RUR")
    gross: Mapped[bool] = mapped_column(Boolean, default=True)

    # Локация
    city: Mapped[str | None] = mapped_column(String, nullable=True)
    area_id: Mapped[str | None] = mapped_column(String, nullable=True)

    # Опыт
    experience_id: Mapped[str | None] = mapped_column(String, nullable=True)
    experience_name: Mapped[str | None] = mapped_column(String, nullable=True)

    # Формат работы
    work_format: Mapped[str] = mapped_column(String, default="ON_SITE")

    # Работодатель
    employer_id: Mapped[str | None] = mapped_column(String, nullable=True)
    company_logo_url: Mapped[str | None] = mapped_column(String, nullable=True)

    def __repr__(self) -> str:
        return f"<VacancyORM(external_id={self.external_id}, name={self.name})>"
