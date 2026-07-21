"""Pytest-фикстуры для тестовых сущностей."""
import pytest
from datetime import datetime, timezone

from shared.domain.entities.vacancy import Vacancy
from shared.domain.entities.resume import Resume
from shared.domain.entities.analysis import Analysis, AnalysisStatus
from shared.domain.entities.vacancy_reply import VacancyReply, VacancyReplyStatus


# --- Фикстуры для Vacancy ---

@pytest.fixture
def vacancy_python() -> Vacancy:
    """Вакансия Python разработчика."""
    return Vacancy(
        external_id="123456",
        name="Python Developer",
        employer_id="789",
        employer_name="Tech Corp",
        requirement="Python, Django, Docker, PostgreSQL",
        responsibility="Разработка бэкенда на Django",
        published_at=datetime.now(timezone.utc),
        url="https://hh.ru/vacancy/123456",
        city="Moscow",
        experience_name="От 1 года до 3 лет",
        work_format="REMOTE",
        salary_from=150000,
        salary_to=200000,
    )


@pytest.fixture
def vacancy_java() -> Vacancy:
    """Вакансия Java разработчика."""
    return Vacancy(
        external_id="789012",
        name="Java Developer",
        employer_id="456",
        employer_name="Soft Corp",
        requirement="Java, Spring, Docker, Kafka",
        responsibility="Разработка микросервисов на Java",
        published_at=datetime.now(timezone.utc),
        url="https://hh.ru/vacancy/789012",
        city="Moscow",
        experience_name="От 3 до 5 лет",
        work_format="ON_SITE",
        salary_from=200000,
        salary_to=250000,
    )


@pytest.fixture
def vacancy_archived() -> Vacancy:
    """Архивная вакансия."""
    return Vacancy(
        external_id="999999",
        name="Archived Vacancy",
        employer_id="000",
        employer_name="Old Corp",
        requirement="Old requirements",
        responsibility="Old responsibilities",
        published_at=datetime.now(timezone.utc),
        url="https://hh.ru/vacancy/999999",
        is_archived=True,
    )


# --- Фикстуры для Resume ---

@pytest.fixture
def resume_python() -> Resume:
    """Резюме Python разработчика."""
    return Resume(
        profession="Python Developer",
        skills=["Python", "Django", "FastAPI", "Docker", "PostgreSQL"],
        full_text="Опыт разработки на Python 5 лет. Работал с Django, FastAPI. Знание Docker, PostgreSQL.",
        is_active=True,
    )


@pytest.fixture
def resume_java() -> Resume:
    """Резюме Java разработчика."""
    return Resume(
        profession="Java Developer",
        skills=["Java", "Spring", "Docker", "Kafka"],
        full_text="Опыт разработки на Java 3 года. Работал с Spring Boot, микросервисы.",
        is_active=True,
    )


@pytest.fixture
def resume_inactive() -> Resume:
    """Неактивное резюме."""
    return Resume(
        profession="Inactive Developer",
        skills=["Python"],
        full_text="Неактивное резюме",
        is_active=False,
    )


# --- Фикстуры для Analysis ---

@pytest.fixture
def analysis_completed() -> Analysis:
    """Завершенный анализ с высокой оценкой."""
    return Analysis(
        vacancy_id="123456",
        resume_id=1,
        match_score=85.5,
        strengths=["Python", "Docker"],
        weaknesses=["No SQL"],
        status=AnalysisStatus.COMPLETED,
    )


@pytest.fixture
def analysis_pending() -> Analysis:
    """Анализ в статусе PENDING."""
    return Analysis(
        vacancy_id="654321",
        resume_id=1,
        status=AnalysisStatus.PENDING,
    )


@pytest.fixture
def analysis_failed() -> Analysis:
    """Анализ со статусом FAILED."""
    return Analysis(
        vacancy_id="987654",
        resume_id=1,
        status=AnalysisStatus.FAILED,
        error_message="Ошибка LLM: превышен таймаут",
        retry_count=1,
    )


# --- Фикстуры для VacancyReply ---

@pytest.fixture
def reply_ready() -> VacancyReply:
    """Отклик со статусом READY."""
    return VacancyReply(
        vacancy_id="123456",
        resume_id=1,
        cover_letter="Здравствуйте! Заинтересовался вашей вакансией...",
        match_score=85.5,
        status=VacancyReplyStatus.READY,
    )


@pytest.fixture
def reply_sent() -> VacancyReply:
    """Отправленный отклик."""
    return VacancyReply(
        vacancy_id="654321",
        resume_id=1,
        cover_letter="Здравствуйте! Заинтересовался вашей вакансией...",
        match_score=85.5,
        status=VacancyReplyStatus.SENT,
        message_id="hh_message_123",
        sent_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def reply_failed() -> VacancyReply:
    """Отклик со статусом FAILED."""
    return VacancyReply(
        vacancy_id="123456",
        resume_id=1,
        cover_letter="Здравствуйте! Заинтересовался вашей вакансией...",
        match_score=85.5,
        status=VacancyReplyStatus.FAILED,
        error_message="Ошибка отправки в HH",
        retry_count=2,
    )


# --- Комплексные фикстуры (связанные сущности) ---

@pytest.fixture
def vacancy_with_resume(vacancy_python, resume_python) -> dict:
    """Словарь с вакансией и резюме для связанных тестов."""
    return {
        "vacancy": vacancy_python,
        "resume": resume_python,
    }


@pytest.fixture
def analysis_with_reply(analysis_completed, reply_ready) -> dict:
    """Словарь с анализом и откликом для связанных тестов."""
    return {
        "analysis": analysis_completed,
        "reply": reply_ready,
    }
