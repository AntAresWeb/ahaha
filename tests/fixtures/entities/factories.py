"""Фабрики для создания тестовых сущностей с кастомными параметрами."""
from datetime import datetime, timezone
from typing import Any

from shared.domain.entities.vacancy import Vacancy
from shared.domain.entities.resume import Resume
from shared.domain.entities.analysis import Analysis, AnalysisStatus
from shared.domain.entities.vacancy_reply import VacancyReply, VacancyReplyStatus


class VacancyFactory:
    """Фабрика для создания тестовых вакансий."""

    @staticmethod
    def create(**kwargs: Any) -> Vacancy:
        """Создать вакансию с кастомными параметрами."""
        defaults = {
            "external_id": "123456",
            "name": "Python Developer",
            "employer_id": "789",
            "employer_name": "Tech Corp",
            "requirement": "Python, Django, Docker",
            "responsibility": "Разработка веб-приложений",
            "published_at": datetime.now(timezone.utc),
            "url": "https://hh.ru/vacancy/123456",
            "city": "Moscow",
            "experience_name": "От 1 года до 3 лет",
            "work_format": "REMOTE",
            "salary_from": 150000,
            "salary_to": 200000,
        }
        defaults.update(kwargs)
        return Vacancy(**defaults)

    @staticmethod
    def create_batch(count: int, **kwargs: Any) -> list[Vacancy]:
        """Создать несколько вакансий с разными external_id."""
        vacancies = []
        base_id = kwargs.pop("external_id", "100000")
        for i in range(count):
            vacancy = VacancyFactory.create(
                external_id=str(int(base_id) + i),
                **kwargs
            )
            vacancies.append(vacancy)
        return vacancies

    @staticmethod
    def create_python_dev(**kwargs: Any) -> Vacancy:
        """Создать вакансию Python разработчика."""
        defaults = {
            "name": "Python Developer",
            "requirement": "Python, Django, Docker, PostgreSQL",
            "responsibility": "Разработка бэкенда на Django",
        }
        defaults.update(kwargs)
        return VacancyFactory.create(**defaults)

    @staticmethod
    def create_java_dev(**kwargs: Any) -> Vacancy:
        """Создать вакансию Java разработчика."""
        defaults = {
            "name": "Java Developer",
            "requirement": "Java, Spring, Docker, Kafka",
            "responsibility": "Разработка микросервисов на Java",
            "experience_name": "От 3 до 5 лет",
        }
        defaults.update(kwargs)
        return VacancyFactory.create(**defaults)


class ResumeFactory:
    """Фабрика для создания тестовых резюме."""

    @staticmethod
    def create(**kwargs: Any) -> Resume:
        """Создать резюме с кастомными параметрами."""
        defaults = {
            "profession": "Python Developer",
            "skills": ["Python", "Docker", "FastAPI"],
            "full_text": "Опыт разработки на Python 5 лет. Работал с Django, FastAPI.",
            "is_active": True,
        }
        defaults.update(kwargs)
        return Resume(**defaults)

    @staticmethod
    def create_batch(count: int, **kwargs: Any) -> list[Resume]:
        """Создать несколько резюме с разными профессиями."""
        resumes = []
        base_profession = kwargs.pop("profession", "Python Developer")
        for i in range(count):
            resume = ResumeFactory.create(
                profession=f"{base_profession} {i+1}",
                **kwargs
            )
            resumes.append(resume)
        return resumes

    @staticmethod
    def create_python_resume(**kwargs: Any) -> Resume:
        """Создать резюме Python разработчика."""
        defaults = {
            "profession": "Python Developer",
            "skills": ["Python", "Django", "FastAPI", "Docker", "PostgreSQL"],
            "full_text": "Опыт разработки на Python 5 лет. Работал с Django, FastAPI. Знание Docker, PostgreSQL.",
        }
        defaults.update(kwargs)
        return ResumeFactory.create(**defaults)


class AnalysisFactory:
    """Фабрика для создания тестовых анализов."""

    @staticmethod
    def create(**kwargs: Any) -> Analysis:
        """Создать анализ с кастомными параметрами."""
        defaults = {
            "vacancy_id": 1,
            "resume_id": 1,
            "match_score": 85.5,
            "strengths": ["Python", "Docker"],
            "weaknesses": ["No SQL"],
            "status": AnalysisStatus.COMPLETED,
        }
        defaults.update(kwargs)
        return Analysis(**defaults)

    @staticmethod
    def create_pending(**kwargs: Any) -> Analysis:
        """Создать анализ со статусом PENDING."""
        return AnalysisFactory.create(status=AnalysisStatus.PENDING, **kwargs)

    @staticmethod
    def create_failed(**kwargs: Any) -> Analysis:
        """Создать анализ со статусом FAILED."""
        return AnalysisFactory.create(
            status=AnalysisStatus.FAILED,
            error_message="Ошибка LLM: превышен таймаут",
            **kwargs
        )

    @staticmethod
    def create_high_score(**kwargs: Any) -> Analysis:
        """Создать анализ с высокой оценкой (> 80)."""
        return AnalysisFactory.create(match_score=92.0, **kwargs)

    @staticmethod
    def create_low_score(**kwargs: Any) -> Analysis:
        """Создать анализ с низкой оценкой (< 50)."""
        return AnalysisFactory.create(match_score=35.0, **kwargs)


class VacancyReplyFactory:
    """Фабрика для создания тестовых откликов."""

    @staticmethod
    def create(**kwargs: Any) -> VacancyReply:
        """Создать отклик с кастомными параметрами."""
        defaults = {
            "vacancy_id": 1,
            "resume_id": 1,
            "cover_letter": "Здравствуйте! Заинтересовался вашей вакансией...",
            "match_score": 85.5,
            "status": VacancyReplyStatus.READY,
        }
        defaults.update(kwargs)
        return VacancyReply(**defaults)

    @staticmethod
    def create_ready(**kwargs: Any) -> VacancyReply:
        """Создать отклик со статусом READY."""
        return VacancyReplyFactory.create(status=VacancyReplyStatus.READY, **kwargs)

    @staticmethod
    def create_sent(**kwargs: Any) -> VacancyReply:
        """Создать отклик со статусом SENT."""
        return VacancyReplyFactory.create(
            status=VacancyReplyStatus.SENT,
            message_id="hh_message_123",
            sent_at=datetime.now(timezone.utc),
            **kwargs
        )

    @staticmethod
    def create_failed(**kwargs: Any) -> VacancyReply:
        """Создать отклик со статусом FAILED."""
        return VacancyReplyFactory.create(
            status=VacancyReplyStatus.FAILED,
            error_message="Ошибка отправки в HH",
            **kwargs
        )
