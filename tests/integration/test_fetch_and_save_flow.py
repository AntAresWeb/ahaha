import pytest
import re
from sqlalchemy.ext.asyncio import AsyncSession

from src.vacancy_analizer.application.usecases.fetch_and_save_vacancies import FetchAndSaveVacanciesUseCase
from src.vacancy_analizer.domain.entities.criteria import Criteria


@pytest.mark.asyncio
async def test_fetch_and_save_flow(
    httpx_mock,
    vacancy_repository,
    hh_source,
    filter_service,
    uow_factory,
    mock_hh_response_multi,
):
    """
    Интеграционный тест: проверяет весь поток от API до БД.
    """
    
    # 1. Мокаем ответ HH.ru
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.hh\.ru/vacancies\?.*"),
        json=mock_hh_response_multi
    )
    
    # 2. Создаём Use Case с фабрикой UoW
    usecase = FetchAndSaveVacanciesUseCase(
        source=hh_source,
        filter_service=filter_service,
        uow_factory=uow_factory,
    )
    
    # 3. Задаём критерии (минимальная зарплата 100 000)
    criteria = Criteria(min_salary=100000)
    
    # 4. Выполняем Use Case
    saved_count = await usecase.execute(keyword="python", criteria=criteria)
    
    # 5. Проверки
    assert saved_count == 1
    
    # Проверяем, что в БД сохранилась только вакансия с высокой зарплатой
    saved_vacancy = await vacancy_repository.get_by_id("1")
    assert saved_vacancy is not None
    assert saved_vacancy.name == "High Salary Python Dev"
    assert saved_vacancy.salary_from == 150000
    
    # Вакансия с низкой зарплатой не сохранена
    missing_vacancy = await vacancy_repository.get_by_id("2")
    assert missing_vacancy is None
