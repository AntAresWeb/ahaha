import logging
from collections.abc import Callable

from src.vacancy_analizer.application.ports.unit_of_work import UnitOfWork
from src.vacancy_analizer.application.ports.vacancy_source import VacancySource
from src.vacancy_analizer.application.services.vacancy_filter import VacancyFilterService
from src.vacancy_analizer.domain.entities.criteria import Criteria

logger = logging.getLogger(__name__)


class FetchAndSaveVacanciesUseCase:
    """
    Сценарий: Получить вакансии из внешнего источника и сохранить подходящие.
    """

    def __init__(
        self,
        source: VacancySource,
        filter_service: VacancyFilterService,
        uow_factory: Callable[[], UnitOfWork],
    ) -> None:
        self.source = source
        self.filter_service = filter_service
        self.uow_factory = uow_factory

    async def execute(self, keyword: str, criteria: Criteria) -> int:
        """
        Выполняет сценарий.
        Args:
            keyword: Ключевое слово для поиска (например, "python")
            criteria: Критерии отбора вакансий
        Returns:
            int: Количество сохранённых вакансий.
        """
        # 1. Получаем вакансии из внешнего источника (все страницы)
        logger.info("Начинаем поиск вакансий по ключевому слову: %s", keyword)
        raw_vacancies = await self.source.search_all_pages(keyword)
        logger.debug("Получено %d вакансий из источника", len(raw_vacancies))

        # 2. Фильтруем по критериям
        relevant_vacancies = self.filter_service.filter_by_criteria(
            raw_vacancies, criteria
        )
        logger.info("После фильтрации осталось %d вакансий", len(relevant_vacancies))

        if not relevant_vacancies:
            return 0

        # 3. Сохраняем через UnitOfWork
        async with self.uow_factory() as uow:
            saved_count = await uow.vacancies.save_batch(relevant_vacancies)
            await uow.commit()
            logger.info("Сохранено %d вакансий", saved_count)
            return saved_count
