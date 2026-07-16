from abc import ABC, abstractmethod

from src.vacancy_analizer.domain.entities.vacancy import Vacancy


class VacancyRepository(ABC):
    """Порт для хранения и поиска вакансий в БД"""

    @abstractmethod
    async def save_batch(self, vacancies: list[Vacancy]) -> int:
        """
        Сохраняет или обновляет список вакансий.
        Возвращает количество успешно обработанных записей.
        """
        ...

    @abstractmethod
    async def get_by_id(self, external_id: str) -> Vacancy | None:
        """Находит вакансию по внешнему ID"""
        ...
