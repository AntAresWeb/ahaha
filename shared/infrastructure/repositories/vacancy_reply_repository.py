"""Адаптер репозитория откликов на вакансии для PostgreSQL."""
import logging

from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from shared.domain.entities.vacancy_reply import VacancyReply, VacancyReplyStatus
from shared.domain.ports.vacancy_reply_repository import VacancyReplyRepository
from shared.infrastructure.mappers.vacancy_reply_mapper import (
    orm_to_vacancy_reply,
    vacancy_reply_to_orm,
)
from shared.infrastructure.models.vacancy_reply import VacancyReplyORM

logger = logging.getLogger(__name__)


class PostgresVacancyReplyRepository(VacancyReplyRepository):
    """Реализация репозитория откликов на PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, reply: VacancyReply) -> VacancyReply:
        """Сохранить или обновить отклик."""
        orm_reply = vacancy_reply_to_orm(reply)
        self._session.add(orm_reply)
        await self._session.flush()
        # Обновляем id в сущности
        reply.id = orm_reply.id
        return reply

    async def get_by_id(self, reply_id: int) -> VacancyReply | None:
        """Получить отклик по ID."""
        result = await self._session.get(VacancyReplyORM, reply_id)
        if result is None:
            return None
        return orm_to_vacancy_reply(result)

    async def get_by_vacancy_and_resume(self, vacancy_id: int, resume_id: int) -> VacancyReply | None:
        """Получить отклик по ID вакансии и резюме."""
        stmt = select(VacancyReplyORM).where(
            VacancyReplyORM.vacancy_id == vacancy_id,
            VacancyReplyORM.resume_id == resume_id,
        )
        result = await self._session.execute(stmt)
        orm_reply = result.scalar_one_or_none()
        if orm_reply is None:
            return None
        return orm_to_vacancy_reply(orm_reply)

    async def get_by_status(self, status: VacancyReplyStatus, limit: int = 100) -> list[VacancyReply]:
        """Получить отклики по статусу."""
        stmt = (
            select(VacancyReplyORM)
            .where(VacancyReplyORM.status == status.value)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        orm_replies = result.scalars().all()
        return [orm_to_vacancy_reply(orm) for orm in orm_replies]

    async def get_ready_to_send(self, limit: int = 100) -> list[VacancyReply]:
        """Получить отклики, готовые к отправке (статус READY)."""
        return await self.get_by_status(VacancyReplyStatus.READY, limit)

    async def get_sent(self, limit: int = 100) -> list[VacancyReply]:
        """Получить отправленные отклики."""
        return await self.get_by_status(VacancyReplyStatus.SENT, limit)

    async def update_status(self, reply_id: int, status: VacancyReplyStatus) -> VacancyReply | None:
        """Обновить статус отклика."""
        stmt = (
            update(VacancyReplyORM)
            .where(VacancyReplyORM.id == reply_id)
            .values(status=status.value)
            .returning(VacancyReplyORM)
        )
        result = await self._session.execute(stmt)
        orm_reply = result.scalar_one_or_none()
        if orm_reply is None:
            return None
        return orm_to_vacancy_reply(orm_reply)

    async def exists_for_vacancy(self, vacancy_id: int) -> bool:
        """Проверить, существует ли отклик для вакансии."""
        stmt = select(exists().where(VacancyReplyORM.vacancy_id == vacancy_id))
        result = await self._session.execute(stmt)
        return result.scalar()
