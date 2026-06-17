import re
import pytest
import httpx

from src.vacancy_analizer.infrastructure.api_clients.hh_client import VacancyFetcher
from src.vacancy_analizer.share.config import get_settings


@pytest.mark.asyncio
async def test_vacancy_fetcher_exists():
    fetcher = VacancyFetcher()
    assert isinstance(fetcher, VacancyFetcher)


@pytest.mark.asyncio
async def test_fetch_sends_required_user_agent_header(httpx_mock):
    """Тест проверяет, что запрос содержит обязательные заголовоки HH-User-Agent"""
    
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.hh\.ru/vacancies\?.*"),
        json={"items": [], "found": 0, "pages": 0, "page": 0}
    )
    
    fetcher = VacancyFetcher()
    await fetcher.fetch(key="python")
    
    request = httpx_mock.get_request()
    assert "HH-User-Agent" in request.headers
    assert request.headers["HH-User-Agent"] == get_settings().hh_app_name


@pytest.mark.asyncio
async def test_fetch_returns_full_response_metadata(httpx_mock):
    """Тест проверяет возврат полной структуры ответа"""
    
    mock_data = {
        "items": [{"id": "123", "name": "Python Dev"}],
        "found": 1,
        "pages": 2,
        "page": 0,
        "per_page": 10
    }
    
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.hh\.ru/vacancies\?.*"),
        json=mock_data
    )
    
    fetcher = VacancyFetcher()
    result = await fetcher.fetch(key="python")
    
    assert result["found"] == 1
    assert result["pages"] == 2
    assert result["items"][0]["id"] == "123"


@pytest.mark.asyncio
async def test_fetch_handles_http_error(httpx_mock):
    """Тест проверяет обработку HTTP-ошибки"""
    
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://api\.hh\.ru/vacancies\?.*"),
        status_code=403,
        text="Forbidden"
    )
    
    fetcher = VacancyFetcher()
    
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        await fetcher.fetch(key="python")
    
    assert exc_info.value.response.status_code == 403

