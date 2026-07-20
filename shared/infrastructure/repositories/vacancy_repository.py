"""Адаптер репозитория вакансий для PostgreSQL."""
import logging

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from shared.domain.entities.vacancy import Vacancy
from shared.domain.ports.vacancy_repository import VacancyRepository
from shared.infrastructure.mappers.vacancy_mapper import (
    orm_to_vacancy,
    vacancy_to_orm_dict,
)
from shared.infrastructure.models.vacancy import VacancyORM

logger = logging.getLogger(__name__)


class PostgresVacancyRepository(VacancyRepository):
    """Реализация репозитория вакансий на PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_batch(self, vacancies: list[Vacancy]) -> int:
        """Сохранить или обновить список вакансий через UPSERT."""
        if not vacancies:
            return 0

        values = [vacancy_to_orm_dict(v) for v in vacancies]

        stmt = insert(VacancyORM).values(values)

        # UPSERT: обновляем все поля при конфликте
        stmt = stmt.on_conflict_do_update(
            constraint="vacancies_pkey",
            set_={
                "name": stmt.excluded.name,
                "employer_name": stmt.excluded.employer_name,
                "requirement": stmt.excluded.requirement,
                "responsibility": stmt.excluded.responsibility,
                "published_at": stmt.excluded.published_at,
                "url": stmt.excluded.url,
                "alternate_url": stmt.excluded.alternate_url,
                "salary_from": stmt.excluded.salary_from,
                "salary_to": stmt.excluded.salary_to,
                "currency": stmt.excluded.currency,
                "gross": stmt.excluded.gross,
                "city": stmt.excluded.city,
                "area_id": stmt.excluded.area_id,
                "experience_id": stmt.excluded.experience_id,
                "experience_name": stmt.excluded.experience_name,
                "work_format": stmt.excluded.work_format,
                "employer_id": stmt.excluded.employer_id,
                "company_logo_url": stmt.excluded.company_logo_url,
                "updated_at": stmt.excluded.updated_at,
            },
        )

        result = await self._session.execute(stmt)
        affected_rows = result.rowcount

        logger.info(f"Сохранено/обновлено вакансий: {affected_rows}")
        return affected_rows

    async def get_by_id(self, external_id: str) -> Vacancy | None:
        """Найти вакансию по внешнему ID."""
        result = await self._session.execute(
            select(VacancyORM).where(VacancyORM.external_id == external_id),
        )
        orm_vacancy = result.scalar_one_or_none()

        if orm_vacancy is None:
            return None

        return orm_to_vacancy(orm_vacancy)

    async def get_pending_for_analysis(self, limit: int = 100) -> list[Vacancy]:
        """Получить вакансии, требующие анализа."""
        # Логика получения вакансий без связанного анализа
        # или с анализом в статусе PENDING
        # TODO: Реализовать после создания AnalysisORM
        return []