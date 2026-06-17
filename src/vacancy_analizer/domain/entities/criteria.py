from dataclasses import dataclass, field

from src.vacancy_analizer.domain.entities.vacancy import Vacancy


@dataclass
class Criteria:
    """
    Критерии отбора вакансий.
    Используется для фильтрации вакансий по требованиям пользователя.
    """
    # Ключевые слова, которые должны присутствовать в описании/требованиях
    keywords: list[str] = field(default_factory=list)

    # Минимальная зарплата (в рублях, если не указана другая валюта)
    min_salary: int | None = None

    # Валюта (по умолчанию RUR)
    currency: str = "RUR"

    # Только вакансии с указанной зарплатой
    only_with_salary: bool = False

    # Только удалённые вакансии (True) / Только офис (False) / Любые (None)
    remote_only: bool | None = None

    # Требуемый опыт работы (id из справочника hh.ru)
    experience_id: str | None = None  # "noExperience", "between1And3", "between3And6" и т.д.

    # Регион (id из справочника hh.ru)
    area_id: str | None = None  # "1" — Москва, "2" — СПб

    # Исключить слова (черный список)
    exclude_keywords: list[str] = field(default_factory=list)


    def is_relevant(self, vacancy: Vacancy) -> bool:
        """Проверяет, соответствует ли вакансия критериям."""
        checks = [
            self._check_keywords(vacancy),
            self._check_excluded_keywords(vacancy),
            self._check_salary(vacancy),
            self._check_work_format(vacancy),
            self._check_experience(vacancy),
            self._check_area(vacancy),
        ]
        return all(checks)


    def _check_keywords(self, vacancy: Vacancy) -> bool:
        """Проверка наличия ключевых слов."""
        if not self.keywords:
            return True
        text = f"{vacancy.requirement} {vacancy.responsibility}".lower()
        return any(kw.lower() in text for kw in self.keywords)


    def _check_excluded_keywords(self, vacancy: Vacancy) -> bool:
        """Проверка отсутствия исключённых слов."""
        if not self.exclude_keywords:
            return True
        text = f"{vacancy.name} {vacancy.requirement} {vacancy.responsibility}".lower()
        return not any(kw.lower() in text for kw in self.exclude_keywords)


    def _check_salary(self, vacancy: Vacancy) -> bool:
        """Проверка зарплатных требований."""
        if self.only_with_salary and vacancy.salary_from is None and vacancy.salary_to is None:
            return False

        if self.min_salary and self.currency == vacancy.currency:
            if vacancy.salary_from and vacancy.salary_from < self.min_salary:
                return False
            if vacancy.salary_to and vacancy.salary_to < self.min_salary:
                return False
        return True


    def _check_work_format(self, vacancy: Vacancy) -> bool:
        """Проверка формата работы."""
        if self.remote_only is True:
            return vacancy.work_format == "REMOTE"
        if self.remote_only is False:
            return vacancy.work_format in ["ON_SITE", "MIXED"]
        return True


    def _check_experience(self, vacancy: Vacancy) -> bool:
        """Проверка опыта работы."""
        if not self.experience_id:
            return True
        return vacancy.experience_id == self.experience_id

    def _check_area(self, vacancy: Vacancy) -> bool:
        """Проверка региона."""
        if not self.area_id:
            return True
        return vacancy.area_id == self.area_id
