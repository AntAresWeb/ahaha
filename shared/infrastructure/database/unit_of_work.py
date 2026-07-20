"""Реализация Unit of Work для PostgreSQL."""
from typing import TYPE_CHECKING, Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from shared.domain.ports.unit_of_work import UnitOfWork, UnitOfWorkFactory
from shared.infrastructure.repositories.analysis_repository import PostgresAnalysisRepository
from shared.infrastructure.repositories.resume_repository import PostgresResumeRepository
from shared.infrastructure.repositories.vacancy_reply_repository import PostgresVacancyReplyRepository
from shared.infrastructure.repositories.vacancy_repository import PostgresVacancyRepository

if TYPE_CHECKING:
    from shared.domain.ports.analysis_repository import AnalysisRepository
    from shared.domain.ports.resume_repository import ResumeRepository
    from shared.domain.ports.vacancy_reply_repository import VacancyReplyRepository
    from shared.domain.ports.vacancy_repository import VacancyRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    """Реализация Unit of Work на SQLAlchemy."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory
        self._session: AsyncSession | None = None
        self.vacancies: VacancyRepository | None = None
        self.resumes: ResumeRepository | None = None
        self.analyses: AnalysisRepository | None = None
        self.vacancy_replies: VacancyReplyRepository | None = None

    async def __aenter__(self) -> Self:
        self._session = self.session_factory()
        self.vacancies = PostgresVacancyRepository(self._session)
        self.resumes = PostgresResumeRepository(self._session)
        self.analyses = PostgresAnalysisRepository(self._session)
        self.vacancy_replies = PostgresVacancyReplyRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        if self._session:
            await self._session.close()

    async def commit(self) -> None:
        if self._session:
            await self._session.commit()

    async def rollback(self) -> None:
        if self._session:
            await self._session.rollback()


def create_uow_factory(
    session_factory: async_sessionmaker[AsyncSession],
) -> UnitOfWorkFactory:
    """
    Создает фабрику для UnitOfWork.

    Returns:
        Callable, который при вызове возвращает новый экземпляр UnitOfWork.
    """
    def _factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory)
    return _factory
