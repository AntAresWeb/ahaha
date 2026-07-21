"""Адаптер репозитория анализов для PostgreSQL."""
import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from shared.domain.entities.analysis import Analysis, AnalysisStatus
from shared.domain.ports.analysis_repository import AnalysisRepository
from shared.infrastructure.mappers.analysis_mapper import (
    analysis_to_orm,
    orm_to_analysis,
)
from shared.infrastructure.models.analysis import AnalysisORM

logger = logging.getLogger(__name__)


class PostgresAnalysisRepository(AnalysisRepository):
    """Реализация репозитория анализов на PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, analysis: Analysis) -> Analysis:
        """Сохранить или обновить анализ."""
        orm_analysis = analysis_to_orm(analysis)
        self._session.add(orm_analysis)
        await self._session.flush()
        # Обновляем id в сущности
        analysis.id = orm_analysis.id
        return analysis

    async def get_by_id(self, analysis_id: int) -> Analysis | None:
        """Получить анализ по ID."""
        result = await self._session.get(AnalysisORM, analysis_id)
        if result is None:
            return None
        return orm_to_analysis(result)

    async def get_by_vacancy_and_resume(self, vacancy_id: str, resume_id: int) -> Analysis | None:
        """Получить анализ по ID вакансии и резюме."""
        stmt = select(AnalysisORM).where(
            AnalysisORM.vacancy_id == vacancy_id,
            AnalysisORM.resume_id == resume_id,
        )
        result = await self._session.execute(stmt)
        orm_analysis = result.scalar_one_or_none()
        if orm_analysis is None:
            return None
        return orm_to_analysis(orm_analysis)

    async def get_pending(self, limit: int = 100) -> list[Analysis]:
        """Получить анализы со статусом PENDING."""
        return await self.get_by_status(AnalysisStatus.PENDING, limit)

    async def get_by_status(self, status: AnalysisStatus, limit: int = 100) -> list[Analysis]:
        """Получить анализы по статусу."""
        stmt = (
            select(AnalysisORM)
            .where(AnalysisORM.status == status.value)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        orm_analyses = result.scalars().all()
        return [orm_to_analysis(orm) for orm in orm_analyses]

    async def update_status(self, analysis_id: int, status: AnalysisStatus) -> Analysis | None:
        """Обновить статус анализа."""
        stmt = (
            update(AnalysisORM)
            .where(AnalysisORM.id == analysis_id)
            .values(status=status.value)
            .returning(AnalysisORM)
        )
        result = await self._session.execute(stmt)
        orm_analysis = result.scalar_one_or_none()
        if orm_analysis is None:
            return None
        return orm_to_analysis(orm_analysis)

    async def get_ready_for_analysis(self, limit: int = 100) -> list[Analysis]:
        """Получить анализы, готовые к обработке (статус PENDING)."""
        return await self.get_pending(limit)
