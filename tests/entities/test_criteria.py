import pytest
from datetime import datetime
from src.vacancy_analizer.domain.entities.vacancy import Vacancy
from src.vacancy_analizer.domain.entities.criteria import Criteria


def test_criteria_matches_by_keywords():
    """Тест проверяет фильтрацию по ключевым словам"""
    
    vacancy = Vacancy(
        external_id="123",
        name="Python Developer",
        employer_name="Test Corp",
        employer_id = "1",
        requirement="Looking for Python and Django expert",
        responsibility="Write code",
        published_at=datetime.now(),
        url="https://test.com/123",
        alternate_url="https://test.com/123"
    )
    
    criteria = Criteria(keywords=["python", "django"])
    
    assert criteria.is_relevant(vacancy) is True


def test_criteria_filters_by_min_salary():
    """Тест проверяет фильтрацию по минимальной зарплате"""
    
    vacancy = Vacancy(
        external_id="123",
        name="Developer",
        employer_name="Test Corp",
        employer_id = "1",
        requirement="",
        responsibility="",
        published_at=datetime.now(),
        url="",
        alternate_url="",
        salary_from=100000
    )
    
    criteria = Criteria(min_salary=120000)
    
    assert criteria.is_relevant(vacancy) is False


def test_criteria_filters_blacklisted_words():
    """Тест проверяет исключение слов"""
    
    vacancy = Vacancy(
        external_id="123",
        name="Junior Python Developer",
        employer_name="Outsource",
        employer_id = "1",
        requirement="Работа в офисе",
        responsibility="",
        published_at=datetime.now(),
        url="",
        alternate_url=""
    )
    
    criteria = Criteria(exclude_keywords=["junior", "office"])
    
    assert criteria.is_relevant(vacancy) is False  # есть "junior"
