"""Порт репозитория откликов на вакансии."""
from abc import ABC, abstractmethod

from shared.domain.entities.vacancy_reply import VacancyReply, VacancyReplyStatus


class VacancyReplyRepository(ABC):
    """Интерфейс репозитория для работы с откликами на вакансии."""

    @abstractmethod
    async def save(self, reply: VacancyReply) -> VacancyReply:
        """
        Сохранить или обновить отклик.

        Args:
            reply: Отклик для сохранения

        Returns:
            Сохраненный отклик (с заполненным id)
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, reply_id: int) -> VacancyReply | None:
        """
        Получить отклик по ID.

        Args:
            reply_id: ID отклика

        Returns:
            VacancyReply или None, если не найдено
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_vacancy_and_resume(self, vacancy_id: int, resume_id: int) -> VacancyReply | None:
        """
        Получить отклик по ID вакансии и резюме.

        Args:
            vacancy_id: ID вакансии
            resume_id: ID резюме

        Returns:
            VacancyReply или None, если не найдено
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_status(self, status: VacancyReplyStatus, limit: int = 100) -> list[VacancyReply]:
        """
        Получить отклики по статусу.

        Args:
            status: Статус для фильтрации
            limit: Максимальное количество

        Returns:
            Список откликов
        """
        raise NotImplementedError

    @abstractmethod
    async def get_ready_to_send(self, limit: int = 100) -> list[VacancyReply]:
        """
        Получить отклики, готовые к отправке (статус READY).

        Args:
            limit: Максимальное количество

        Returns:
            Список откликов
        """
        raise NotImplementedError

    @abstractmethod
    async def get_sent(self, limit: int = 100) -> list[VacancyReply]:
        """
        Получить отправленные отклики.

        Args:
            limit: Максимальное количество

        Returns:
            Список отправленных откликов
        """
        raise NotImplementedError

    @abstractmethod
    async def update_status(self, reply_id: int, status: VacancyReplyStatus) -> VacancyReply | None:
        """
        Обновить статус отклика.

        Args:
            reply_id: ID отклика
            status: Новый статус

        Returns:
            Обновленный отклик или None, если не найден
        """
        raise NotImplementedError

    @abstractmethod
    async def exists_for_vacancy(self, vacancy_id: int) -> bool:
        """
        Проверить, существует ли отклик для вакансии.

        Args:
            vacancy_id: ID вакансии

        Returns:
            True если отклик существует
        """
        raise NotImplementedError
