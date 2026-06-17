from abc import ABC, abstractmethod

from src.vacancy_analizer.domain.entities.vacancy import Vacancy


class VacancyRepository(ABC):
    """Порт для хранения и поиска вакансий в БД"""

    @abstractmethod
    async def save(self, vacancy: Vacancy) -> bool:
        """
        Сохраняет вакансию, если её ещё нет.
        Returns:
            bool: True если вакансия сохранена, False если дубликат.
        """
        ...

    @abstractmethod
    async def get_by_id(self, external_id: str) -> Vacancy | None:
        """Находит вакансию по внешнему ID"""
        ...
