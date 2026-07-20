"""Порт репозитория анализов."""
from abc import ABC, abstractmethod

from shared.domain.entities.analysis import Analysis, AnalysisStatus


class AnalysisRepository(ABC):
    """Интерфейс репозитория для работы с анализами."""

    @abstractmethod
    async def save(self, analysis: Analysis) -> Analysis:
        """
        Сохранить или обновить анализ.

        Args:
            analysis: Анализ для сохранения

        Returns:
            Сохраненный анализ (с заполненным id)
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, analysis_id: int) -> Analysis | None:
        """
        Получить анализ по ID.

        Args:
            analysis_id: ID анализа

        Returns:
            Analysis или None, если не найдено
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_vacancy_and_resume(self, vacancy_id: int, resume_id: int) -> Analysis | None:
        """
        Получить анализ по ID вакансии и резюме.

        Args:
            vacancy_id: ID вакансии
            resume_id: ID резюме

        Returns:
            Analysis или None, если не найдено
        """
        raise NotImplementedError

    @abstractmethod
    async def get_pending(self, limit: int = 100) -> list[Analysis]:
        """
        Получить анализы со статусом PENDING.

        Args:
            limit: Максимальное количество

        Returns:
            Список анализов
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_status(self, status: AnalysisStatus, limit: int = 100) -> list[Analysis]:
        """
        Получить анализы по статусу.

        Args:
            status: Статус для фильтрации
            limit: Максимальное количество

        Returns:
            Список анализов
        """
        raise NotImplementedError

    @abstractmethod
    async def update_status(self, analysis_id: int, status: AnalysisStatus) -> Analysis | None:
        """
        Обновить статус анализа.

        Args:
            analysis_id: ID анализа
            status: Новый статус

        Returns:
            Обновленный анализ или None, если не найден
        """
        raise NotImplementedError

    @abstractmethod
    async def get_ready_for_analysis(self, limit: int = 100) -> list[Analysis]:
        """
        Получить анализы, готовые к обработке (статус PENDING).

        Args:
            limit: Максимальное количество

        Returns:
            Список анализов
        """
        raise NotImplementedError
