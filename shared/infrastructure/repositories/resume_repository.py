"""Адаптер репозитория резюме для PostgreSQL."""
import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from shared.domain.entities.resume import Resume
from shared.domain.ports.resume_repository import ResumeRepository
from shared.infrastructure.mappers.resume_mapper import (
    orm_to_resume,
    resume_to_orm,
    resume_to_orm_dict,
)
from shared.infrastructure.models.resume import ResumeORM

logger = logging.getLogger(__name__)


class PostgresResumeRepository(ResumeRepository):
    """Реализация репозитория резюме на PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session


    async def save(self, resume: Resume) -> Resume:
        """Сохранить или обновить резюме."""
        if resume.id is None:
            orm_resume = resume_to_orm(resume)
            self._session.add(orm_resume)
            await self._session.flush()
            resume.id = orm_resume.id
            return resume

        update_data = resume_to_orm_dict(resume)

        stmt = (
            update(ResumeORM)
            .where(ResumeORM.id == resume.id)
            .values(**update_data)
            .returning(ResumeORM)
        )

        result = await self._session.execute(stmt)
        orm_resume = result.scalar_one_or_none()

        if orm_resume is None:
            raise ValueError(f"Резюме с id {resume.id} не найдено")

        return orm_to_resume(orm_resume)


    async def get_by_id(self, resume_id: int) -> Resume | None:
        """Получить резюме по ID."""
        stmt = select(ResumeORM).where(ResumeORM.id == resume_id)
        result = await self._session.execute(stmt)
        orm_resume = result.scalar_one_or_none()
        if orm_resume is None:
            return None
        return orm_to_resume(orm_resume)


    async def get_by_hh_id(self, hh_resume_id: str) -> Resume | None:
        """Получить резюме по ID из HH."""
        stmt = select(ResumeORM).where(ResumeORM.hh_resume_id == hh_resume_id)
        result = await self._session.execute(stmt)
        orm_resume = result.scalar_one_or_none()
        if orm_resume is None:
            return None
        return orm_to_resume(orm_resume)


    async def list_active(self) -> list[Resume]:
        """Получить все активные резюме."""
        stmt = select(ResumeORM).where(ResumeORM.is_active)
        result = await self._session.execute(stmt)
        orm_resumes = result.scalars().all()
        return [orm_to_resume(orm) for orm in orm_resumes]


    async def get_by_profession(self, profession: str) -> list[Resume]:
        """Получить резюме по профессии."""
        stmt = select(ResumeORM).where(ResumeORM.profession == profession)
        result = await self._session.execute(stmt)
        orm_resumes = result.scalars().all()
        return [orm_to_resume(orm) for orm in orm_resumes]


    async def delete(self, resume_id: int) -> bool:
        """Мягкое удаление резюме."""
        stmt = (
            update(ResumeORM)
            .where(ResumeORM.id == resume_id)
            .values(is_active=False)
            .returning(ResumeORM.id)
        )
        result = await self._session.execute(stmt)
        deleted_id = result.scalar_one_or_none()
        return deleted_id is not None
