from typing import TYPE_CHECKING, Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.vacancy_analizer.application.ports.unit_of_work import UnitOfWork, UnitOfWorkFactory
from src.vacancy_analizer.infrastructure.db.repositories.vacancy_repository import PostgresVacancyRepository

if TYPE_CHECKING:
    from src.vacancy_analizer.application.ports.vacancy_repository import VacancyRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory
        self._session: AsyncSession | None = None
        self.vacancies: VacancyRepository | None = None

    async def __aenter__(self) -> Self:
        self._session = self.session_factory()
        # Внутри создаём конкретный репозиторий, но сохраняем под интерфейсом
        self.vacancies = PostgresVacancyRepository(self._session)
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
    Возвращает callable, который при вызове возвращает новый экземпляр UnitOfWork.
    """
    def _factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory)
    return _factory
