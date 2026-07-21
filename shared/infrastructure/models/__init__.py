"""ORM-модели для базы данных."""

from .analysis import AnalysisORM
from .base import Base
from .resume import ResumeORM
from .vacancy import VacancyORM
from .vacancy_reply import VacancyReplyORM

__all__ = [
    "AnalysisORM",
    "Base",
    "ResumeORM",
    "VacancyORM",
    "VacancyReplyORM",
]
