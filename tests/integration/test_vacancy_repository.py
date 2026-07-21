"""Интеграционные тесты для VacancyRepository."""
import pytest

from shared.domain.entities.vacancy import Vacancy
from shared.infrastructure.repositories.vacancy_repository import PostgresVacancyRepository
from tests.fixtures.entities.factories import VacancyFactory


@pytest.mark.asyncio
async def test_save_batch_creates_vacancies(test_session):
    """Тест: сохранение новых вакансий."""
    repo = PostgresVacancyRepository(test_session)
    vacancies = VacancyFactory.create_batch(3)
    
    # Act
    count = await repo.save_batch(vacancies)
    
    # Assert
    assert count == 3
    for vacancy in vacancies:
        saved = await repo.get_by_id(vacancy.external_id)
        assert saved is not None
        assert saved.external_id == vacancy.external_id
        assert saved.name == vacancy.name


@pytest.mark.asyncio
async def test_save_batch_updates_existing_vacancies(test_session, vacancy_python):
    """Тест: обновление существующих вакансий (UPSERT)."""
    repo = PostgresVacancyRepository(test_session)
    
    # Сохраняем вакансию
    await repo.save_batch([vacancy_python])
    saved = await repo.get_by_id(vacancy_python.external_id)
    assert saved.name == "Python Developer"
    
    # Обновляем вакансию
    updated_vacancy = VacancyFactory.create(
        external_id=vacancy_python.external_id,
        name="Senior Python Developer",
        salary_to=250000
    )
    await repo.save_batch([updated_vacancy])
    
    # Проверяем обновление
    updated = await repo.get_by_id(vacancy_python.external_id)
    assert updated is not None
    assert updated.name == "Senior Python Developer"
    assert updated.salary_to == 250000


@pytest.mark.asyncio
async def test_save_batch_empty_list(test_session):
    """Тест: сохранение пустого списка."""
    repo = PostgresVacancyRepository(test_session)
    
    # Act
    count = await repo.save_batch([])
    
    # Assert
    assert count == 0


@pytest.mark.asyncio
async def test_get_by_id_found(test_session, vacancy_python):
    """Тест: получение существующей вакансии."""
    repo = PostgresVacancyRepository(test_session)
    await repo.save_batch([vacancy_python])
    
    # Act
    result = await repo.get_by_id(vacancy_python.external_id)
    
    # Assert
    assert result is not None
    assert result.external_id == vacancy_python.external_id
    assert result.name == vacancy_python.name
    assert result.employer_name == vacancy_python.employer_name
    assert result.city == vacancy_python.city
    assert result.salary_from == vacancy_python.salary_from
    assert result.salary_to == vacancy_python.salary_to


@pytest.mark.asyncio
async def test_get_by_id_not_found(test_session):
    """Тест: получение несуществующей вакансии."""
    repo = PostgresVacancyRepository(test_session)
    
    # Act
    result = await repo.get_by_id("non_existent_id")
    
    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_get_pending_for_analysis_returns_list(test_session, vacancy_python):
    """Тест: получение вакансий для анализа."""
    repo = PostgresVacancyRepository(test_session)
    await repo.save_batch([vacancy_python])
    
    # Act
    result = await repo.get_pending_for_analysis(limit=10)
    
    # Assert
    # TODO: Реализовать когда появится связь с Analysis
    assert isinstance(result, list)
