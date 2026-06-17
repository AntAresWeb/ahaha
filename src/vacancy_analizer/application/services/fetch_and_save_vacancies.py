from src.vacancy_analizer.application.ports.vacancy_repository import VacancyRepository
from src.vacancy_analizer.application.ports.vacancy_source import VacancySource
from src.vacancy_analizer.application.services.vacancy_filter import VacancyFilterService
from src.vacancy_analizer.domain.entities.criteria import Criteria
from src.vacancy_analizer.domain.entities.vacancy import Vacancy


class FetchAndSaveVacanciesUseCase:
    """
    Сценарий: Получить вакансии из внешнего источника и сохранить подходящие.
    """

    def __init__(
        self,
        source: VacancySource,
        repository: VacancyRepository,
        filter_service: VacancyFilterService,
    ) -> None:
        self.source = source
        self.repository = repository
        self.filter_service = filter_service


    async def execute(self, keyword: str, criteria: Criteria) -> int:
        """
        Выполняет сценарий.

        Args:
            keyword: Ключевое слово для поиска (например, "python")
            criteria: Критерии отбора вакансий

        Returns:
            int: Количество сохранённых вакансий.
        """
        # 1. Получаем вакансии из внешнего источника
        raw_vacancies = await self.source.search_by_keyword(keyword)

        # 2. Фильтруем по критериям
        relevant_vacancies = self.filter_service.filter_by_criteria(
            raw_vacancies, criteria,
        )

        # 3. Сохраняем только релевантные (проверяем дубли внутри)
        saved_count = 0
        for vacancy in relevant_vacancies:
            if await self.repository.save(vacancy):
                saved_count += 1

        return saved_count
