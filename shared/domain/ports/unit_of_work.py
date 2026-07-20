"""Порт Unit of Work."""
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Self

from shared.domain.ports.vacancy_repository import VacancyRepository
from shared.domain.ports.resume_repository import ResumeRepository
from shared.domain.ports.analysis_repository import AnalysisRepository
from shared.domain.ports.vacancy_reply_repository import VacancyReplyRepository


class UnitOfWork(ABC):
    """
    Интерфейс Unit of Work.

    Обеспечивает транзакционную согласованность между репозиториями.
    """

    vacancies: VacancyRepository
    resumes: ResumeRepository
    analyses: AnalysisRepository
    vacancy_replies: VacancyReplyRepository

    @abstractmethod
    async def __aenter__(self) -> Self:
        """Вход в контекстный менеджер."""
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Выход из контекстного менеджера с автоматическим commit/rollback."""
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        """Зафиксировать транзакцию."""
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        """Откатить транзакцию."""
        raise NotImplementedError


# Тип для фабрики UnitOfWork
UnitOfWorkFactory = Callable[[], Awaitable[UnitOfWork]]
