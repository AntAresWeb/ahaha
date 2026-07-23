"""Фабрики для создания тестовых сущностей и связанных наборов данных."""
from datetime import datetime, timezone
from typing import Any

from shared.domain.entities.vacancy import Vacancy
from shared.domain.entities.resume import Resume
from shared.domain.entities.analysis import Analysis, AnalysisStatus
from shared.domain.entities.vacancy_reply import VacancyReply, VacancyReplyStatus


# 1. Фабрики отдельных сущностей
class VacancyFactory:
    """Фабрика для создания тестовых вакансий."""

    @staticmethod
    def create(**kwargs: Any) -> Vacancy:
        """Создать вакансию с кастомными параметрами."""
        defaults = {
            "external_id": kwargs.get("external_id", "123456"),
            "url": "https://hh.ru/vacancy/123456",
            "name": "Python Developer",
            "employer_id": "789",
            "employer_name": "Tech Corp",
            "requirement": "Python, Django, Docker",
            "responsibility": "Разработка веб-приложений",
            "published_at": datetime.now(timezone.utc),
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


class ResumeFactory:
    """Фабрика для создания тестовых резюме."""

    @staticmethod
    def create(**kwargs: Any) -> Resume:
        """Создать резюме с кастомными параметрами."""
        defaults = {
            "profession": "Python Developer",
            "skills": ["Python", "Docker", "FastAPI"],
            "full_text": "Опыт разработки на Python 5 лет.",
            "is_active": True,
        }
        defaults.update(kwargs)
        return Resume(**defaults)

    @staticmethod
    def create_batch(count: int, **kwargs: Any) -> list[Resume]:
        """Создать несколько резюме."""
        resumes = []
        base_profession = kwargs.pop("profession", "Python Developer")
        for i in range(count):
            resume = ResumeFactory.create(
                profession=f"{base_profession} {i+1}",
                **kwargs
            )
            resumes.append(resume)
        return resumes


class AnalysisFactory:
    """Фабрика для создания тестовых анализов."""

    @staticmethod
    def create(
        vacancy_id: str = "123456",
        resume_id: int = 1,
        **kwargs: Any,
    ) -> Analysis:
        """Создать анализ с привязкой к вакансии и резюме."""
        defaults = {
            "vacancy_id": vacancy_id,
            "resume_id": resume_id,
            "match_score": 85.5,
            "strengths": ["Python", "Docker"],
            "weaknesses": ["No SQL"],
            "status": AnalysisStatus.COMPLETED,
        }
        defaults.update(kwargs)
        return Analysis(**defaults)

    @staticmethod
    def create_pending(vacancy_id: str = "123456", resume_id: int = 1, **kwargs: Any) -> Analysis:
        """Создать анализ со статусом PENDING."""
        return AnalysisFactory.create(
            vacancy_id=vacancy_id,
            resume_id=resume_id,
            status=AnalysisStatus.PENDING,
            **kwargs,
        )


class VacancyReplyFactory:
    """Фабрика для создания тестовых откликов."""

    @staticmethod
    def create(
        vacancy_id: str = "123456",
        resume_id: int = 1,
        analysis_id: int | None = None,
        **kwargs: Any,
    ) -> VacancyReply:
        """Создать отклик с привязкой к вакансии, резюме и анализу."""
        defaults = {
            "vacancy_id": vacancy_id,
            "resume_id": resume_id,
            "analysis_id": analysis_id,
            "cover_letter": "Здравствуйте! Заинтересовался вашей вакансией...",
            "match_score": 85.5,
            "status": VacancyReplyStatus.READY,
        }
        defaults.update(kwargs)
        return VacancyReply(**defaults)

    @staticmethod
    def create_ready(vacancy_id: str = "123456", resume_id: int = 1, **kwargs: Any) -> VacancyReply:
        """Создать отклик со статусом READY."""
        return VacancyReplyFactory.create(
            vacancy_id=vacancy_id,
            resume_id=resume_id,
            status=VacancyReplyStatus.READY,
            **kwargs,
        )


# 2. Фабрики для создания ПОЛНЫХ наборов связанных данных
class TestDataFactory:
    """
    Фабрика для создания ПОЛНОГО набора связанных данных.
    Возвращает словарь со всеми созданными сущностями.
    """

    @staticmethod
    async def create_full_analysis_set(
        vacancy_kwargs: dict | None = None,
        resume_kwargs: dict | None = None,
        analysis_kwargs: dict | None = None,
    ) -> dict[str, Any]:
        """
        Создает полный набор данных: Vacancy → Resume → Analysis.
        Возвращает словарь с сущностями.
        """
        vacancy_kwargs = vacancy_kwargs or {}
        resume_kwargs = resume_kwargs or {}
        analysis_kwargs = analysis_kwargs or {}

        vacancy = VacancyFactory.create(**vacancy_kwargs)
        resume = ResumeFactory.create(**resume_kwargs)
        analysis = AnalysisFactory.create(
            vacancy_id=vacancy.external_id,
            resume_id=resume.id or 1,
            **analysis_kwargs,
        )

        return {
            "vacancy": vacancy,
            "resume": resume,
            "analysis": analysis,
        }

    @staticmethod
    async def create_full_reply_set(
        vacancy_kwargs: dict | None = None,
        resume_kwargs: dict | None = None,
        analysis_kwargs: dict | None = None,
        reply_kwargs: dict | None = None,
    ) -> dict[str, Any]:
        """
        Создает полный набор данных: Vacancy → Resume → Analysis → VacancyReply.
        Возвращает словарь с сущностями.
        """
        base_data = await TestDataFactory.create_full_analysis_set(
            vacancy_kwargs=vacancy_kwargs,
            resume_kwargs=resume_kwargs,
            analysis_kwargs=analysis_kwargs,
        )

        vacancy = base_data["vacancy"]
        resume = base_data["resume"]
        analysis = base_data["analysis"]

        reply_kwargs = reply_kwargs or {}
        reply = VacancyReplyFactory.create(
            vacancy_id=vacancy.external_id,
            resume_id=resume.id or 1,
            analysis_id=analysis.id,
            **reply_kwargs,
        )

        base_data["reply"] = reply
        return base_data

    @staticmethod
    async def save_full_analysis_set(
        session,
        vacancy_kwargs: dict | None = None,
        resume_kwargs: dict | None = None,
        analysis_kwargs: dict | None = None,
    ) -> dict[str, Any]:
        """
        Создает И СОХРАНЯЕТ в БД полный набор данных.
        Возвращает словарь с сохраненными сущностями.
        """
        from shared.infrastructure.repositories import (
            PostgresVacancyRepository,
            PostgresResumeRepository,
            PostgresAnalysisRepository,
        )

        # 1. Создаем данные
        data = await TestDataFactory.create_full_analysis_set(
            vacancy_kwargs=vacancy_kwargs,
            resume_kwargs=resume_kwargs,
            analysis_kwargs=analysis_kwargs,
        )

        # 2. Сохраняем вакансию
        vacancy_repo = PostgresVacancyRepository(session)
        await vacancy_repo.save_batch([data["vacancy"]])

        # 3. Сохраняем резюме
        resume_repo = PostgresResumeRepository(session)
        saved_resume = await resume_repo.save(data["resume"])
        data["resume"] = saved_resume

        # 4. Обновляем анализ с реальным resume_id
        data["analysis"].resume_id = saved_resume.id

        # 5. Сохраняем анализ
        analysis_repo = PostgresAnalysisRepository(session)
        saved_analysis = await analysis_repo.save(data["analysis"])
        data["analysis"] = saved_analysis

        return data

    @staticmethod
    async def save_full_reply_set(
        session,
        vacancy_kwargs: dict | None = None,
        resume_kwargs: dict | None = None,
        analysis_kwargs: dict | None = None,
        reply_kwargs: dict | None = None,
    ) -> dict[str, Any]:
        """
        Создает И СОХРАНЯЕТ в БД полный набор данных: 
        Vacancy → Resume → Analysis → VacancyReply.
        Возвращает словарь с сохраненными сущностями.
        """
        from shared.infrastructure.repositories import (
            PostgresVacancyRepository,
            PostgresResumeRepository,
            PostgresAnalysisRepository,
            PostgresVacancyReplyRepository,
        )

        # 1. Создаем базовые данные
        data = await TestDataFactory.create_full_reply_set(
            vacancy_kwargs=vacancy_kwargs,
            resume_kwargs=resume_kwargs,
            analysis_kwargs=analysis_kwargs,
            reply_kwargs=reply_kwargs,
        )

        # 2. Сохраняем вакансию
        vacancy_repo = PostgresVacancyRepository(session)
        await vacancy_repo.save_batch([data["vacancy"]])

        # 3. Сохраняем резюме
        resume_repo = PostgresResumeRepository(session)
        saved_resume = await resume_repo.save(data["resume"])
        data["resume"] = saved_resume

        # 4. Обновляем анализ с реальным resume_id
        data["analysis"].resume_id = saved_resume.id

        # 5. Сохраняем анализ
        analysis_repo = PostgresAnalysisRepository(session)
        saved_analysis = await analysis_repo.save(data["analysis"])
        data["analysis"] = saved_analysis

        # 6. Обновляем отклик с реальным analysis_id
        data["reply"].analysis_id = saved_analysis.id
        data["reply"].resume_id = saved_resume.id

        # 7. Сохраняем отклик
        reply_repo = PostgresVacancyReplyRepository(session)
        saved_reply = await reply_repo.save(data["reply"])
        data["reply"] = saved_reply

        return data
    