# tests/integration/test_fetch_and_save_flow.py
import pytest
import re
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.vacancy_analizer.infrastructure.db.models.base import Base
from src.vacancy_analizer.infrastructure.db.repositories.vacancy_repository import PostgresVacancyRepository
from src.vacancy_analizer.infrastructure.api_clients.hh_source import HHVacancySource
from src.vacancy_analizer.application.usecases.fetch_and_save_vacancies import FetchAndSaveVacanciesUseCase
from src.vacancy_analizer.application.services.vacancy_filter import VacancyFilterService
from src.vacancy_analizer.domain.entities.criteria import Criteria
from src.vacancy_analizer.domain.entities.vacancy import Vacancy


@pytest.fixture(scope="function")
def db_session() -> AsyncSession:
    """Создает временную базу данных SQLite в памяти."""
    import asyncio
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
async def test_fetch_and_save_flow(httpx_mock, db_session: AsyncSession):
    """
    Интеграционный тест: проверяет весь поток от API до БД.
    
    Сценарий:
    1. Мокаем ответ HH.ru с двумя вакансиями
    2. Создаём Use Case с реальными адаптерами
    3. Выполняем Use Case с критерием (минимальная зарплата 100000)
    4. Проверяем, что в БД сохранилась только подходящая вакансия
    """
    
    # 1. Мокаем ответ HH.ru
    mock_response = {
        "items": [
            {
                "id": "1",
                "name": "High Salary Python Dev",
                "employer": {"name": "Big Corp"},
                "salary": {"from": 150000, "to": 200000, "currency": "RUR", "gross": False},
                "address": {"city": "Moscow"},
                "experience": {"id": "between1And3", "name": "От 1 года до 3 лет"},
                "snippet": {
                    "requirement": "Python, Django, PostgreSQL",
                    "responsibility": "Write clean code"
                },
                "published_at": "2026-06-18T12:00:00+0300",
                "alternate_url": "https://hh.ru/vacancy/1",
                "work_format": [{"id": "REMOTE", "name": "Удалённая работа"}],
                "area": {"id": "1", "name": "Москва"}
            },
            {
                "id": "2",
                "name": "Low Salary Python Dev",
                "employer": {"name": "Small Corp"},
                "salary": {"from": 50000, "to": 70000, "currency": "RUR", "gross": True},
                "address": {"city": "SPB"},
                "experience": {"id": "noExperience", "name": "Нет опыта"},
                "snippet": {
                    "requirement": "Basic Python",
                    "responsibility": "Fix bugs"
                },
                "published_at": "2026-06-18T12:00:00+0300",
                "alternate_url": "https://hh.ru/vacancy/2",
                "work_format": [{"id": "ON_SITE", "name": "В офисе"}],
                "area": {"id": "2", "name": "СПб"}
            }
        ],
        "found": 2,
        "pages": 1,
        "page": 0,
        "per_page": 20
    }
    
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.hh\.ru/vacancies\?.*"),
        json=mock_response
    )
    
    # 2. Создаём адаптеры
    source = HHVacancySource(user_agent="TestApp/1.0 (test@example.com)")
    repository = PostgresVacancyRepository(db_session)
    filter_service = VacancyFilterService()
    
    # 3. Создаём Use Case
    usecase = FetchAndSaveVacanciesUseCase(
        source=source,
        repository=repository,
        filter_service=filter_service
    )
    
    # 4. Задаём критерии (минимальная зарплата 100 000)
    criteria = Criteria(min_salary=100000)
    
    # 5. Выполняем Use Case
    saved_count = await usecase.execute(keyword="python", criteria=criteria)
    
    # 6. Проверки
    assert saved_count == 1  # Сохранена только вакансия с зарплатой 150000
    
    # Проверяем, что в БД действительно одна вакансия
    saved_vacancy = await repository.get_by_id("1")
    assert saved_vacancy is not None
    assert saved_vacancy.name == "High Salary Python Dev"
    assert saved_vacancy.salary_from == 150000
    
    # Вакансия с низкой зарплатой не сохранена
    missing_vacancy = await repository.get_by_id("2")
    assert missing_vacancy is None
