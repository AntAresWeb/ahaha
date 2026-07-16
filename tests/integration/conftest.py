import pytest

from src.vacancy_analizer.infrastructure.api_clients.hh_source import HHVacancySource
from src.vacancy_analizer.application.services.vacancy_filter import VacancyFilterService


@pytest.fixture
def mock_hh_response_single():
    """Мок ответа HH.ru с одной вакансией."""
    return {
        "items": [
            {
                "id": "1",
                "name": "Python Developer",
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
            }
        ],
        "found": 1,
        "pages": 1,
        "page": 0,
        "per_page": 20
    }


@pytest.fixture
def mock_hh_response_multi():
    """Мок ответа HH.ru с двумя вакансиями (высокая и низкая зарплата)."""
    return {
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


@pytest.fixture
def hh_source():
    """Фикстура для HHVacancySource."""
    return HHVacancySource(user_agent="TestApp/1.0 (test@example.com)")


@pytest.fixture
def filter_service():
    """Фикстура для VacancyFilterService."""
    return VacancyFilterService()