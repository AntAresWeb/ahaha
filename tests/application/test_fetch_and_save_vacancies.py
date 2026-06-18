import pytest
from unittest.mock import AsyncMock
from datetime import datetime
from src.vacancy_analizer.domain.entities.vacancy import Vacancy
from src.vacancy_analizer.domain.entities.criteria import Criteria
from src.vacancy_analizer.application.usecases.fetch_and_save_vacancies import FetchAndSaveVacanciesUseCase
from src.vacancy_analizer.application.services.vacancy_filter import VacancyFilterService
from src.vacancy_analizer.application.ports.vacancy_source import VacancySource
from src.vacancy_analizer.application.ports.vacancy_repository import VacancyRepository


@pytest.mark.asyncio
async def test_usecase_saves_only_relevant_vacancies():
    """
    Сценарий: Пользователь ищет вакансии по ключевому слову "python" 
    с минимальной зарплатой 100000.
    
    Ожидаемый результат: Из двух найденных вакансий сохраняется только одна,
    потому что у второй зарплата ниже порога.
    """
    
    # 1. Создаём тестовые данные
    criteria = Criteria(min_salary=100000)
    
    # 2. Создаём список вакансий, которые вернёт мок-источник
    vacancy_high_salary = Vacancy(
        external_id="1",
        name="Python Developer (High Salary)",
        employer_name="Tech Corp",
        employer_id = "1",
        requirement="Python, Django, PostgreSQL",
        responsibility="Write clean code",
        published_at=datetime(2026, 6, 10, 12, 0, 0),
        url="https://test.com/1",
        alternate_url="https://test.com/alt/1",
        salary_from=150000,
        salary_to=200000,
        currency="RUR",
        gross=False,
        city="Москва",
        area_id="1",
        experience_id="between1And3",
        experience_name="От 1 года до 3 лет",
        work_format="REMOTE"
    )
    
    vacancy_low_salary = Vacancy(
        external_id="2",
        name="Python Developer (Low Salary)",
        employer_name="Small Startup",
        employer_id = "2",
        requirement="Basic Python",
        responsibility="Fix bugs",
        published_at=datetime(2026, 6, 10, 12, 0, 0),
        url="https://test.com/2",
        alternate_url="https://test.com/alt/2",
        salary_from=50000,
        salary_to=70000,
        currency="RUR",
        gross=True,
        city="Санкт-Петербург",
        area_id="2",
        experience_id="noExperience",
        experience_name="Нет опыта",
        work_format="ON_SITE"
    )
    
    # 3. Создаём моки для портов
    mock_source = AsyncMock(spec=VacancySource)
    mock_source.search_by_keyword.return_value = [vacancy_high_salary, vacancy_low_salary]
    
    mock_repository = AsyncMock(spec=VacancyRepository)
    mock_repository.save.return_value = True
    
    # 4. Создаём реальный сервис фильтрации (не мок, потому что это логика)
    filter_service = VacancyFilterService()
    
    # 5. Создаём Use Case с внедрёнными зависимостями
    usecase = FetchAndSaveVacanciesUseCase(
        source=mock_source,
        repository=mock_repository,
        filter_service=filter_service
    )
    
    # 6. Выполняем Use Case
    saved_count = await usecase.execute(keyword="python", criteria=criteria)
    
    # 7. Проверки (Ассерты)
    # - Сохранена только одна вакансия (с высокой зарплатой)
    assert saved_count == 1
    
    # - Проверяем, что источник был вызван с правильным ключевым словом
    mock_source.search_by_keyword.assert_called_once_with("python")
    
    # - Проверяем, что репозиторий был вызван только один раз
    assert mock_repository.save.call_count == 1
    
    # - Проверяем, что сохранена именно вакансия с высокой зарплатой
    saved_vacancy = mock_repository.save.call_args[0][0]
    assert saved_vacancy.external_id == "1"
    assert saved_vacancy.salary_from == 150000


@pytest.mark.asyncio
async def test_usecase_does_not_save_duplicates():
    """
    Сценарий: Вакансия уже существует в БД.
    
    Ожидаемый результат: Use Case не пытается сохранить дубликат.
    Репозиторий возвращает False, и Use Case учитывает это.
    """
    
    # 1. Создаём тестовые данные
    criteria = Criteria(min_salary=100000)
    existing_vacancy = Vacancy(
        external_id="1",
        name="Python Developer",
        employer_name="Tech Corp",
        employer_id = "1",
        requirement="Python",
        responsibility="Write code",
        published_at=datetime(2026, 6, 10, 12, 0, 0),
        url="",
        alternate_url="",
        salary_from=150000,
        salary_to=200000,
        currency="RUR",
        gross=False,
        city="Москва",
        area_id="1"
    )
    
    # 2. Мокаем источник
    mock_source = AsyncMock(spec=VacancySource)
    mock_source.search_by_keyword.return_value = [existing_vacancy]
    
    # 3. Мокаем репозиторий: save возвращает False (дубликат)
    mock_repository = AsyncMock(spec=VacancyRepository)
    mock_repository.save.return_value = False
    
    # 4. Создаём Use Case
    filter_service = VacancyFilterService()
    usecase = FetchAndSaveVacanciesUseCase(
        source=mock_source,
        repository=mock_repository,
        filter_service=filter_service
    )
    
    # 5. Выполняем Use Case
    saved_count = await usecase.execute(keyword="python", criteria=criteria)
    
    # 6. Проверки
    assert saved_count == 0  # Ничего не сохранено
    mock_repository.save.assert_called_once_with(existing_vacancy)


@pytest.mark.asyncio
async def test_usecase_handles_empty_response():
    """
    Сценарий: Внешний источник не нашёл ни одной вакансии.
    
    Ожидаемый результат: Use Case возвращает 0, репозиторий не вызывается.
    """
    
    # 1. Мокаем источник: возвращает пустой список
    mock_source = AsyncMock(spec=VacancySource)
    mock_source.search_by_keyword.return_value = []
    
    # 2. Мокаем репозиторий
    mock_repository = AsyncMock(spec=VacancyRepository)
    
    # 3. Создаём Use Case
    filter_service = VacancyFilterService()
    usecase = FetchAndSaveVacanciesUseCase(
        source=mock_source,
        repository=mock_repository,
        filter_service=filter_service
    )
    
    # 4. Выполняем Use Case
    criteria = Criteria(min_salary=100000)
    saved_count = await usecase.execute(keyword="python", criteria=criteria)
    
    # 5. Проверки
    assert saved_count == 0
    mock_source.search_by_keyword.assert_called_once_with("python")
    mock_repository.save.assert_not_called()  # Репозиторий не вызывался


@pytest.mark.asyncio
async def test_usecase_handles_source_error():
    """
    Сценарий: Внешний источник выбрасывает исключение.
    
    Ожидаемый результат: Use Case пробрасывает исключение выше.
    """
    
    # 1. Мокаем источник: выбрасывает исключение
    mock_source = AsyncMock(spec=VacancySource)
    mock_source.search_by_keyword.side_effect = Exception("API connection error")
    
    # 2. Мокаем репозиторий
    mock_repository = AsyncMock(spec=VacancyRepository)
    
    # 3. Создаём Use Case
    filter_service = VacancyFilterService()
    usecase = FetchAndSaveVacanciesUseCase(
        source=mock_source,
        repository=mock_repository,
        filter_service=filter_service
    )
    
    # 4. Проверяем, что Use Case пробрасывает исключение
    criteria = Criteria(min_salary=100000)
    with pytest.raises(Exception, match="API connection error"):
        await usecase.execute(keyword="python", criteria=criteria)
    
    # 5. Репозиторий не должен вызываться
    mock_repository.save.assert_not_called()
