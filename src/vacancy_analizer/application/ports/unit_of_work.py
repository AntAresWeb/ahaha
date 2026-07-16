from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Self

from src.vacancy_analizer.application.ports.vacancy_repository import VacancyRepository


class UnitOfWork(ABC):
    vacancies: VacancyRepository

    @abstractmethod
    async def __aenter__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> Self:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError

UnitOfWorkFactory = Callable[[], Awaitable[UnitOfWork]]
