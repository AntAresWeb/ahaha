import asyncio
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.vacancy_analizer.infrastructure.db.models.base import Base
from src.vacancy_analizer.infrastructure.db.repositories.vacancy_repository import PostgresVacancyRepository
from src.vacancy_analizer.domain.entities.vacancy import Vacancy


@pytest.fixture(scope="function")
def db_session() -> AsyncSession:
    """Создает временную базу данных SQLite в памяти."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    asyncio.run(create_tables())
    
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    session = async_session()
    
    yield session
    
    async def cleanup():
        await session.close()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()
    
    asyncio.run(cleanup())


@pytest.mark.asyncio
async def test_repository_saves_new_vacancy(db_session: AsyncSession):
    """Тест проверяет сохранение новой вакансии."""
    
    vacancy = Vacancy(
        external_id="12345",
        name="Python Developer",
        employer_name="Tech Corp",
        requirement="Python, Django, PostgreSQL",
        responsibility="Write clean code",
        published_at=datetime(2026, 6, 18, 12, 0, 0),
        url="https://test.com/vacancy/12345",
        alternate_url="https://test.com/alt/12345",
        salary_from=150000,
        salary_to=200000,
        currency="RUR",
        gross=False,
        city="Moscow",
        area_id="1",
        experience_id="between1And3",
        experience_name="От 1 года до 3 лет",
        work_format="REMOTE",
        employer_id="123",
        company_logo_url="https://test.com/logo.png"
    )
    
    repo = PostgresVacancyRepository(db_session)
    saved = await repo.save(vacancy)
    
    assert saved is True
    
    found = await repo.get_by_id("12345")

    assert found is not None
    assert found.external_id == vacancy.external_id
    assert found.name == vacancy.name
    assert found.employer_name == vacancy.employer_name
    assert found.salary_from == vacancy.salary_from
    assert found.salary_to == vacancy.salary_to
    assert found.city == vacancy.city
    assert found.work_format == vacancy.work_format


@pytest.mark.asyncio
async def test_repository_prevents_duplicates(db_session):
    """Тест проверяет, что дубликаты не сохраняются."""
    
    vacancy = Vacancy(
        external_id="12345",
        name="Python Developer",
        employer_id="1",
        employer_name="Tech Corp",
        requirement="Python",
        responsibility="Code",
        published_at=datetime.now(),
        url="",
        alternate_url="",
    )
    
    repo = PostgresVacancyRepository(db_session)

    first_save = await repo.save(vacancy)
    assert first_save is True
    
    second_save = await repo.save(vacancy)
    assert second_save is False


@pytest.mark.asyncio
async def test_repository_returns_none_for_missing_vacancy(db_session):
    """Тест проверяет, что get_by_id возвращает None для несуществующей вакансии."""
    
    repo = PostgresVacancyRepository(db_session)
    found = await repo.get_by_id("nonexistent")
    assert found is None
