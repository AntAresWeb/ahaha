import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from shared.infrastructure.models.base import Base
from shared.infrastructure.database.unit_of_work import create_uow_factory


@pytest.fixture
async def test_engine():
    """Асинхронная фикстура: создаёт тестовый движок SQLite."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=NullPool,
    )
    
    # Создаём таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Очистка после теста
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def session_factory(test_engine):
    """Асинхронная фикстура: фабрика сессий."""
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


@pytest.fixture
async def db_session(session_factory):
    """Асинхронная фикстура: сессия для тестов."""
    async with session_factory() as session:
        yield session


@pytest.fixture
async def uow_factory(session_factory):
    """Фабрика UnitOfWork для тестов."""
    return create_uow_factory(session_factory)


@pytest.fixture
async def vacancy_repository(db_session):
    """Асинхронная фикстура: репозиторий вакансий."""
    from src.vacancy_analizer.infrastructure.db.repositories.vacancy_repository import PostgresVacancyRepository
    return PostgresVacancyRepository(db_session)
