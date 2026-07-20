"""Порт репозитория резюме."""
from abc import ABC, abstractmethod

from shared.domain.entities.resume import Resume


class ResumeRepository(ABC):
    """Интерфейс репозитория для работы с резюме."""

    @abstractmethod
    async def save(self, resume: Resume) -> Resume:
        """
        Сохранить или обновить резюме.

        Args:
            resume: Резюме для сохранения

        Returns:
            Сохраненное резюме (с заполненным id)
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, resume_id: int) -> Resume | None:
        """
        Получить резюме по ID.

        Args:
            resume_id: ID резюме

        Returns:
            Resume или None, если не найдено
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_hh_id(self, hh_resume_id: str) -> Resume | None:
        """
        Получить резюме по ID из HH.

        Args:
            hh_resume_id: ID резюме в HH

        Returns:
            Resume или None, если не найдено
        """
        raise NotImplementedError

    @abstractmethod
    async def list_active(self) -> list[Resume]:
        """
        Получить все активные резюме.

        Returns:
            Список активных резюме
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_profession(self, profession: str) -> list[Resume]:
        """
        Получить резюме по профессии.

        Args:
            profession: Название профессии

        Returns:
            Список резюме
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, resume_id: int) -> bool:
        """
        Удалить резюме (мягкое удаление).

        Args:
            resume_id: ID резюме

        Returns:
            True если удалено, False если не найдено
        """
        raise NotImplementedError
