import pytest
from unittest.mock import AsyncMock

from src.vacancy_analizer.domain.entities.criteria import Criteria
from src.vacancy_analizer.domain.entities.vacancy import Vacancy
from datetime import datetime
from shared.config.hh_api import HHAPISettings


@pytest.fixture
def test_settings():
    """Фикстура с тестовыми настройками (без чтения реального .env)"""
    return HHAPISettings(
        hh_app_name="test_app/1.0 (test@example.com)",
        hh_app_id="test_app_id",
        hh_app_secret="test_app_secret",
        hh_redirect_uri="http://localhost:9999/auth/callback",
        token_file="test_tokens.json",
    )


@pytest.fixture
def sample_vacancy() -> Vacancy:
    """Базовая фикстура с вакансией для тестов."""
    return Vacancy(
        external_id="test_123",
        name="Test Vacancy",
        employer_name="Test Employer",
        requirement="Python, Django, PostgreSQL",
        responsibility="Write clean code",
        published_at=datetime(2026, 6, 18, 12, 0, 0),
        url="https://test.com",
        alternate_url="https://test.com/alt",
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
        company_logo_url=None,
    )


@pytest.fixture
def sample_criteria() -> Criteria:
    """Базовая фикстура с критериями."""
    return Criteria(min_salary=100000, remote_only=True)


@pytest.fixture
def mock_vacancy_source() -> AsyncMock:
    """Мок для VacancySource."""
    source = AsyncMock()
    source.search_by_keyword.return_value = []
    source.search_all_pages.return_value = []
    return source


@pytest.fixture
def mock_vacancy_repository() -> AsyncMock:
    """Мок для VacancyRepository."""
    repo = AsyncMock()
    repo.save.return_value = True
    repo.save_batch.return_value = 0
    repo.get_by_id.return_value = None
    return repo