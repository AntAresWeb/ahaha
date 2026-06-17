# tests/application/test_fetch_and_save_vacancies.py
import pytest
from unittest.mock import AsyncMock
from datetime import datetime
from src.vacancy_analizer.domain.entities.vacancy import Vacancy
from src.vacancy_analizer.domain.entities.criteria import Criteria
from src.vacancy_analizer.application.services.fetch_and_save_vacancies import FetchAndSaveVacanciesUseCase
from src.vacancy_analizer.application.services.vacancy_filter import VacancyFilterService


@pytest.mark.asyncio
async def test_fetch_and_save_relevant_vacancies():
    """Тест проверяет, что Use Case сохраняет только подходящие вакансии"""
    
    # 1. Создаём мок-источник (VacancySource)
    mock_source = AsyncMock()
    mock_source.search_by_keyword.return_value = [
        Vacancy(
            external_id="1",
            name="High Salary Python Dev",
            employer_name="Big Corp",
            requirement="Python, Django",
            responsibility="Write code",
            published_at=datetime.now(),
            url="",
            alternate_url="",
            salary_from=150000,
            salary_to=200000,
            currency="RUR",
            gross=False,
            city="Москва",
            area_id="1",
            work_format="REMOTE"
        ),
        Vacancy(
            external_id="2",
            name="Low Salary Python Dev",
            employer_name="Small Corp",
            requirement="Python",
            responsibility="Fix bugs",
            published_at=datetime.now(),
            url="",
            alternate_url="",
            salary_from=50000,
            salary_to=70000,
            currency="RUR",
            gross=True,
            city="СПб",
            area_id="2"
        )
    ]
    
    # 2. Создаём мок-репозиторий (VacancyRepository)
    mock_repo = AsyncMock()
    mock_repo.save.return_value = True
    
    # 3. Создаём Criteria (минимальная зарплата 100 000)
    criteria = Criteria(min_salary=100000)
    
    # 4. Создаём Use Case с моками
    filter_service = VacancyFilterService()
    usecase = FetchAndSaveVacanciesUseCase(
        source=mock_source,
        repository=mock_repo,
        filter_service=filter_service
    )
    
    # 5. Выполняем Use Case
    saved_count = await usecase.execute(keyword="python", criteria=criteria)
    
    # 6. Проверки
    assert saved_count == 1  # Сохранена только первая вакансия
    
    # Проверяем, что search был вызван с правильным параметром
    mock_source.search_by_keyword.assert_called_once_with("python")
    
    # Проверяем, что save был вызван только для первой вакансии
    assert mock_repo.save.call_count == 1
    saved_vacancy = mock_repo.save.call_args[0][0]
    assert saved_vacancy.external_id == "1"