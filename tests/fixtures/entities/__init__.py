"""Фикстуры и фабрики для тестов."""

from .factories import (
    VacancyFactory,
    ResumeFactory,
    AnalysisFactory,
    VacancyReplyFactory,
)

from .examples import (
    vacancy_python,
    vacancy_java,
    vacancy_archived,
    resume_python,
    resume_java,
    resume_inactive,
    analysis_completed,
    analysis_pending,
    analysis_failed,
    reply_ready,
    reply_sent,
    reply_failed,
    vacancy_with_resume,
    analysis_with_reply,
)

__all__ = [
    # Фабрики
    "VacancyFactory",
    "ResumeFactory",
    "AnalysisFactory",
    "VacancyReplyFactory",
    # Фикстуры Vacancy
    "vacancy_python",
    "vacancy_java",
    "vacancy_archived",
    # Фикстуры Resume
    "resume_python",
    "resume_java",
    "resume_inactive",
    # Фикстуры Analysis
    "analysis_completed",
    "analysis_pending",
    "analysis_failed",
    # Фикстуры VacancyReply
    "reply_ready",
    "reply_sent",
    "reply_failed",
    # Комплексные фикстуры
    "vacancy_with_resume",
    "analysis_with_reply",
]
