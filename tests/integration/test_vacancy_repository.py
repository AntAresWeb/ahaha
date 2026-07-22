"""Интеграционные тесты для VacancyRepository."""
import pytest

from shared.infrastructure.repositories.vacancy_repository import PostgresVacancyRepository
from tests.fixtures.entities.factories import VacancyFactory


@pytest.mark.asyncio
async def test_save_batch_creates_vacancies(test_session):
    """Тест: сохранение новых вакансий."""
    repo = PostgresVacancyRepository(test_session)
    vacancies = VacancyFactory.create_batch(3)
    
    count = await repo.save_batch(vacancies)
    
    assert count == 3
    for vacancy in vacancies:
        saved = await repo.get_by_id(vacancy.external_id)
        assert saved is not None
        assert saved.external_id == vacancy.external_id
        assert saved.name == vacancy.name


@pytest.mark.asyncio
async def test_save_batch_updates_existing_vacancies(test_session):
    """Тест: обновление существующих вакансий (UPSERT)."""
    repo = PostgresVacancyRepository(test_session)
    vacancy = VacancyFactory.create(name="Python Developer")

    # Сохраняем вакансию
    await repo.save_batch([vacancy])
    saved = await repo.get_by_id(vacancy.external_id)
    assert saved.name == "Python Developer"
    
    # Обновляем вакансию
    updated_vacancy = VacancyFactory.create(
        external_id=vacancy.external_id,
        name="Senior Python Developer",
        salary_to=500000
    )
    await repo.save_batch([updated_vacancy])
    
    # Проверяем обновление
    updated = await repo.get_by_id(vacancy.external_id)
    assert updated is not None
    assert updated.name == "Senior Python Developer"
    assert updated.salary_to == 500000


@pytest.mark.asyncio
async def test_save_batch_empty_list(test_session):
    """Тест: сохранение пустого списка."""
    repo = PostgresVacancyRepository(test_session)
    
    count = await repo.save_batch([])
    assert count == 0


@pytest.mark.asyncio
async def test_get_by_id_found(test_session):
    """Тест: получение существующей вакансии."""
    repo = PostgresVacancyRepository(test_session)
    vacancy = VacancyFactory.create(name="Python Developer")
    await repo.save_batch([vacancy])
    
    result = await repo.get_by_id(vacancy.external_id)
    
    assert result is not None
    assert result.external_id == vacancy.external_id
    assert result.name == vacancy.name
    assert result.employer_name == vacancy.employer_name
    assert result.city == vacancy.city
    assert result.salary_from == vacancy.salary_from
    assert result.salary_to == vacancy.salary_to


@pytest.mark.asyncio
async def test_get_by_id_not_found(test_session):
    """Тест: получение несуществующей вакансии."""
    repo = PostgresVacancyRepository(test_session)
    
    result = await repo.get_by_id("non_existent_id")
    
    assert result is None
