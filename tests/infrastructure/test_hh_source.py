import pytest
import re
from datetime import datetime

import httpx

from src.vacancy_analizer.infrastructure.api_clients.hh_source import HHVacancySource
from src.vacancy_analizer.domain.entities.vacancy import Vacancy


@pytest.mark.asyncio
async def test_hh_source_returns_vacancies(httpx_mock):
    """Тест проверяет, что HHVacancySource правильно парсит ответ API"""
    
    # 1. Мокаем ответ от HH.ru (реальный JSON из твоего файла)
    mock_response = {
        "items": [{
            "id": "133473143",
            "name": "Python-разработчик (Django)",
            "employer": {"name": "Shtab"},
            "salary": {"from": 150000, "to": 180000, "currency": "RUR", "gross": False},
            "address": {"city": "Санкт-Петербург"},
            "experience": {"id": "between1And3", "name": "От 1 года до 3 лет"},
            "snippet": {
                "requirement": "Уверенные знания Python, Django, DRF, PostgreSQL, Celery",
                "responsibility": "Разрабатывать новые функции в сервисе Shtab"
            },
            "published_at": "2026-06-09T15:41:51+0300",
            "alternate_url": "https://hh.ru/vacancy/133473143",
            "work_format": [{"id": "REMOTE", "name": "Удалённая работа"}],
            "area": {"id": "2", "name": "Санкт-Петербург"}
        }],
        "found": 1,
        "pages": 1,
        "page": 0,
        "per_page": 20
    }
    
    # 2. Регистрируем мок-ответ для httpx
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.hh\.ru/vacancies\?.*"),
        json=mock_response
    )
    
    # 3. Создаём адаптер
    source = HHVacancySource()
    
    # 4. Выполняем метод
    vacancies = await source.search_by_keyword("python")
    
    # 5. Проверки
    assert len(vacancies) == 1
    vacancy = vacancies[0]
    
    assert vacancy.external_id == "133473143"
    assert vacancy.name == "Python-разработчик (Django)"
    assert vacancy.employer_name == "Shtab"
    assert vacancy.salary_from == 150000
    assert vacancy.salary_to == 180000
    assert vacancy.currency == "RUR"
    assert vacancy.gross is False
    assert vacancy.city == "Санкт-Петербург"
    assert vacancy.experience_id == "between1And3"
    assert vacancy.experience_name == "От 1 года до 3 лет"
    assert "Python" in vacancy.requirement
    assert "функции" in vacancy.responsibility
    assert vacancy.published_at.replace(tzinfo=None) == datetime(2026, 6, 9, 15, 41, 51)
    assert vacancy.alternate_url == "https://hh.ru/vacancy/133473143"
    assert vacancy.work_format == "REMOTE"
    assert vacancy.area_id == "2"


@pytest.mark.asyncio
async def test_hh_source_handles_empty_response(httpx_mock):
    """Тест проверяет, что адаптер корректно обрабатывает ответ без вакансий"""
    
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.hh\.ru/vacancies\?.*"),
        json={"items": [], "found": 0, "pages": 0, "page": 0, "per_page": 20}
    )
    
    source = HHVacancySource()
    vacancies = await source.search_by_keyword("nonexistent")
    
    assert len(vacancies) == 0


@pytest.mark.asyncio
async def test_hh_source_handles_missing_fields(httpx_mock):
    """Тест проверяет, что адаптер корректно обрабатывает отсутствие необязательных полей"""
    
    mock_response = {
        "items": [{
            "id": "123",
            "name": "Developer",
            "employer": {"name": "Test Corp"},
            # Остальные поля отсутствуют!
        }],
        "found": 1,
        "pages": 1,
        "page": 0,
        "per_page": 20
    }
    
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.hh\.ru/vacancies\?.*"),
        json=mock_response
    )
    
    source = HHVacancySource()
    vacancies = await source.search_by_keyword("python")
    
    assert len(vacancies) == 1
    vacancy = vacancies[0]
    
    assert vacancy.external_id == "123"
    assert vacancy.name == "Developer"
    assert vacancy.employer_name == "Test Corp"
    assert vacancy.salary_from is None
    assert vacancy.salary_to is None
    assert vacancy.city is None
    assert vacancy.work_format == "ON_SITE"


@pytest.mark.asyncio
async def test_hh_source_parses_datetime_correctly(httpx_mock):
    """
    Тест проверяет, что дата публикации парсится корректно,
    даже если часовой пояс указан в формате +0300.
    """
    
    # Мокаем ответ с конкретной датой
    mock_response = {
        "items": [{
            "id": "123",
            "name": "Test",
            "employer": {"name": "Test Corp"},
            "published_at": "2026-06-09T15:41:51+0300",
            # Остальные поля минимальны
        }],
        "found": 1,
        "pages": 1,
        "page": 0,
        "per_page": 20
    }
    
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.hh\.ru/vacancies\?.*"),
        json=mock_response
    )
    
    source = HHVacancySource()
    vacancies = await source.search_by_keyword("python")
    
    assert len(vacancies) == 1
    vacancy = vacancies[0]
    
    # Проверяем, что дата распарсилась правильно
    expected = datetime(2026, 6, 9, 15, 41, 51)
    # Сравниваем только дату и время (игнорируем часовой пояс)
    assert vacancy.published_at.replace(tzinfo=None) == expected


@pytest.mark.asyncio
async def test_hh_source_handles_pagination(httpx_mock):
    """
    Тест проверяет, что адаптер может получать разные страницы.
    """
    
    # Первая страница
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.hh\.ru/vacancies\?.*page=0.*"),
        json={
            "items": [{"id": "1", "name": "Page 1", "employer": {"name": "Test"}}],
            "found": 3,
            "pages": 2,
            "page": 0,
            "per_page": 1
        }
    )
    
    # Вторая страница
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.hh\.ru/vacancies\?.*page=1.*"),
        json={
            "items": [{"id": "2", "name": "Page 2", "employer": {"name": "Test"}}],
            "found": 3,
            "pages": 2,
            "page": 1,
            "per_page": 1
        }
    )
    
    source = HHVacancySource(per_page=1)
    
    # Получаем первую страницу
    page0 = await source.search_by_keyword("python", page=0)
    assert len(page0) == 1
    assert page0[0].external_id == "1"
    
    # Получаем вторую страницу
    page1 = await source.search_by_keyword("python", page=1)
    assert len(page1) == 1
    assert page1[0].external_id == "2"


@pytest.mark.asyncio
async def test_hh_source_gets_all_pages(httpx_mock):
    """
    Тест проверяет, что адаптер может получить все страницы автоматически.
    """
    
    # Страница 0
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.hh\.ru/vacancies\?.*page=0.*"),
        json={
            "items": [{"id": "1", "name": "First", "employer": {"name": "Test"}}],
            "found": 2,
            "pages": 2,
            "page": 0,
            "per_page": 1
        }
    )
    
    # Страница 1
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.hh\.ru/vacancies\?.*page=1.*"),
        json={
            "items": [{"id": "2", "name": "Second", "employer": {"name": "Test"}}],
            "found": 2,
            "pages": 2,
            "page": 1,
            "per_page": 1
        }
    )

    # Страница 2
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.hh\.ru/vacancies\?.*page=1.*"),
        json={
            "items": [],
            "found": 2,
            "pages": 2,
            "page": 1,
            "per_page": 1
        }
    )
    
    source = HHVacancySource(per_page=1)
    
    # Получаем все страницы
    all_vacancies = await source.search_all_pages("python")
    
    assert len(all_vacancies) == 2
    assert all_vacancies[0].external_id == "1"
    assert all_vacancies[1].external_id == "2"


@pytest.mark.asyncio
async def test_hh_source_handles_network_timeout(httpx_mock):
    """Тест проверяет, что адаптер правильно обрабатывает таймаут"""
    
    httpx_mock.add_exception(httpx.TimeoutException("Connection timeout"))
    
    source = HHVacancySource()
    
    with pytest.raises(httpx.TimeoutException):
        await source.search_by_keyword("python")


@pytest.mark.asyncio
async def test_hh_source_handles_http_error(httpx_mock):
    """Тест проверяет, что адаптер правильно обрабатывает HTTP ошибки"""
    
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.hh\.ru/vacancies\?.*"),
        status_code=429,
        text="Too Many Requests"
    )
    
    source = HHVacancySource()
    
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        await source.search_by_keyword("python")
    
    assert exc_info.value.response.status_code == 429


@pytest.mark.asyncio
async def test_hh_source_handles_invalid_json(httpx_mock):
    """Тест проверяет, что адаптер правильно обрабатывает невалидный JSON"""
    
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.hh\.ru/vacancies\?.*"),
        text="<html>Error 500</html>"
    )
    
    source = HHVacancySource()
    
    with pytest.raises(Exception):  # Может быть json.JSONDecodeError или httpx.HTTPStatusError
        await source.search_by_keyword("python")


@pytest.mark.asyncio
async def test_hh_source_accepts_search_params(httpx_mock):
    """Тест проверяет, что адаптер передаёт параметры поиска в API"""
    
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.hh\.ru/vacancies\?.*"),
        json={"items": [], "found": 0, "pages": 0, "page": 0, "per_page": 20}
    )
    
    source = HHVacancySource()
    
    await source.search_by_keyword(
        keyword="python",
        page=2,
        area_id="1",  # Москва
        experience_id="between1And3",
        only_with_salary=True
    )
    
    # Проверяем, что параметры были отправлены
    request = httpx_mock.get_request()
    params = dict(request.url.params)
    
    assert params["text"] == "python"
    assert params["page"] == "2"
    assert params["area"] == "1"
    assert params["experience"] == "between1And3"
    assert params["only_with_salary"] == "true"