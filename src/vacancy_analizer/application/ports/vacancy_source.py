from abc import ABC, abstractmethod

from src.vacancy_analizer.domain.entities.vacancy import Vacancy


class VacancySource(ABC):
    """Порт для получения вакансий из внешнего источника"""

    @abstractmethod
    async def search_by_keyword(self, keyword: str) -> list[Vacancy]:
        """
        Выполняет поиск вакансий по ключевому слову.
        Returns:
            List[Vacancy]: Список вакансий (без фильтрации).
        """
        ...
