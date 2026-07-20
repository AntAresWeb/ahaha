import logging

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.vacancy_analizer.application.ports.vacancy_repository import VacancyRepository
from src.vacancy_analizer.domain.entities.vacancy import Vacancy
from shared.infrastructure.mappers.vacancy_mapper import orm_to_vacancy, vacancy_to_orm_dict
from shared.infrastructure.models.vacancy import VacancyORM

logger = logging.getLogger(__name__)


class PostgresVacancyRepository(VacancyRepository):
    """Адаптер для хранения вакансий в PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session


    async def save_batch(self, vacancies: list[Vacancy]) -> int:
        """Сохраняет или обновляет список вакансий через UPSERT."""

        if not vacancies:
            return 0

        values = [vacancy_to_orm_dict(v) for v in vacancies]
        stmt = insert(VacancyORM).values(values)

        stmt = stmt.on_conflict_do_update(
            constraint="vacancies_pkey",
            set_={
                "name": stmt.excluded.name,
                "employer_name": stmt.excluded.employer_name,
                "salary_from": stmt.excluded.salary_from,
                "salary_to": stmt.excluded.salary_to,
                "updated_at": stmt.excluded.updated_at,
                # Остальные поля аналогично
            },
        )

        result = await self._session.execute(stmt)

        affected_rows = result.rowcount
        logger.info(f"Сохранено/обновлено вакансий: {affected_rows}")
        return affected_rows


    async def get_by_id(self, external_id: str) -> Vacancy | None:
        """Находит вакансию по внешнему ID."""
        result = await self._session.execute(
            select(VacancyORM).where(VacancyORM.external_id == external_id),
        )
        orm_vacancy = result.scalar_one_or_none()

        if orm_vacancy is None:
            return None

        return orm_to_vacancy(orm_vacancy)
