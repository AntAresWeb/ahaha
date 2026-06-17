from src.vacancy_analizer.domain.entities.criteria import Criteria
from src.vacancy_analizer.domain.entities.vacancy import Vacancy


class VacancyFilterService:
    """Сервис фильтрации вакансий (сценарий use case)"""

    def filter_by_criteria(self, vacancies: list[Vacancy], criteria: Criteria) -> list[Vacancy]:
        """Отбирает вакансии, соответствующие критериям."""
        return [v for v in vacancies if criteria.is_relevant(v)]

    def sort_by_salary_desc(self, vacancies: list[Vacancy]) -> list[Vacancy]:
        """Сортирует вакансии по убыванию зарплаты."""
        def get_salary(vacancy: Vacancy) -> int:
            # Берём зарплату "от" или "до", если нет — 0
            if vacancy.salary_from:
                return vacancy.salary_from
            if vacancy.salary_to:
                return vacancy.salary_to
            return 0

        return sorted(vacancies, key=get_salary, reverse=True)
