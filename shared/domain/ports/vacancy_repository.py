"""Порт репозитория вакансий."""
from abc import ABC, abstractmethod

from shared.domain.entities.vacancy import Vacancy


class VacancyRepository(ABC):
    """Интерфейс репозитория для работы с вакансиями."""

    @abstractmethod
    async def save_batch(self, vacancies: list[Vacancy]) -> int:
        """
        Сохранить или обновить список вакансий.

        Args:
            vacancies: Список вакансий для сохранения

        Returns:
            Количество успешно сохраненных записей
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, external_id: str) -> Vacancy | None:
        """
        Получить вакансию по внешнему ID.

        Args:
            external_id: ID вакансии в HH

        Returns:
            Vacancy или None, если не найдена
        """
        raise NotImplementedError

    @abstractmethod
    async def get_pending_for_analysis(self, limit: int = 100) -> list[Vacancy]:
        """
        Получить вакансии, требующие анализа.

        Args:
            limit: Максимальное количество

        Returns:
            Список вакансий
        """
        raise NotImplementedError
