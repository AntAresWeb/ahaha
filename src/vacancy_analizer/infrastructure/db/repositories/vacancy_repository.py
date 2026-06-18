import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.vacancy_analizer.application.ports.vacancy_repository import VacancyRepository
from src.vacancy_analizer.domain.entities.vacancy import Vacancy
from src.vacancy_analizer.infrastructure.db.mappers.vacancy_mapper import orm_to_vacancy, vacancy_to_orm
from src.vacancy_analizer.infrastructure.db.models.vacancy import VacancyORM

logger = logging.getLogger(__name__)


class PostgresVacancyRepository(VacancyRepository):
    """Адаптер для хранения вакансий в PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session


    async def save(self, vacancy: Vacancy) -> bool:
        """
        Сохраняет вакансию в БД.
        Returns:
            bool: True если сохранена, False если дубликат.
        """
        # Проверяем, существует ли уже
        existing = await self.get_by_id(vacancy.external_id)
        if existing:
            logger.debug(f"Вакансия {vacancy.external_id} уже существует")
            return False

        # Преобразуем в ORM и сохраняем
        orm_vacancy = vacancy_to_orm(vacancy)
        self._session.add(orm_vacancy)
        await self._session.commit()

        logger.info(f"Сохранена вакансия {vacancy.external_id}: {vacancy.name}")
        return True


    async def get_by_id(self, external_id: str) -> Vacancy | None:
        """Находит вакансию по внешнему ID."""
        result = await self._session.execute(
            select(VacancyORM).where(VacancyORM.external_id == external_id),
        )
        orm_vacancy = result.scalar_one_or_none()

        if orm_vacancy is None:
            return None

        return orm_to_vacancy(orm_vacancy)
