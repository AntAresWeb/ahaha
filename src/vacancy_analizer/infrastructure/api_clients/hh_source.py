import logging
import re
from datetime import datetime, timezone
from typing import Any

import httpx

from src.vacancy_analizer.application.ports.vacancy_source import VacancySource
from src.vacancy_analizer.domain.entities.vacancy import Vacancy

logger = logging.getLogger(__name__)


class HHVacancySource(VacancySource):
    """
    Адаптер для получения вакансий из API HH.ru.
    Реализует порт VacancySource.
    """

    def __init__(
        self,
        base_url: str = "https://api.hh.ru",
        user_agent: str = "VacancyAnalyzer/1.0 (davydov.a@mail.ru)",
        per_page: int = 20,
        timeout: int = 30,
    ) -> None:
        self.base_url = base_url
        self.user_agent = user_agent
        self.per_page = min(per_page, 100)  # Ограничение API HH.ru
        self.timeout = timeout


    async def search_by_keyword(
        self,
        keyword: str,
        page: int = 0,
        area_id: str | None = None,
        experience_id: str | None = None,
        only_with_salary: bool = False,
    ) -> list[Vacancy]:
        """
        Выполняет поиск вакансий по ключевому слову с дополнительными параметрами.
        Args:
            keyword: Ключевое слово для поиска
            page: Номер страницы (0-based)
            area_id: ID региона (например, "1" для Москвы)
            experience_id: ID опыта (например, "between1And3")
            only_with_salary: Только вакансии с указанной зарплатой
        """
        url = f"{self.base_url}/vacancies"
        params = {
            "text": keyword,
            "per_page": self.per_page,
            "page": page
        }

        if area_id:
            params["area"] = area_id
        if experience_id:
            params["experience"] = experience_id
        if only_with_salary:
            params["only_with_salary"] = "true"

        headers = {"HH-User-Agent": self.user_agent}

        logger.debug(f"Запрос к HH.ru: {url} с параметрами {params}")
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()

                data = response.json()
                raw_items = data.get("items", [])

                logger.debug(f"Получено {len(raw_items)} вакансий (страница {page})")

                return [self._parse_vacancy(item) for item in raw_items]

        except httpx.TimeoutException as e:
            logger.error(f"Таймаут при запросе к HH.ru: {e}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP ошибка {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}", exc_info=True)
            raise


    async def search_all_pages(self, keyword: str, max_pages: int = 10) -> list[Vacancy]:
        """
        Получает все страницы с вакансиями до max_pages.
        Args:
            keyword: Ключевое слово для поиска
            max_pages: Максимальное количество страниц (защита от бесконечного цикла)
        Returns:
            list[Vacancy]: Все вакансии со всех страниц
        """
        all_vacancies = []
        current_page = 0

        while current_page < max_pages:
            # Получаем одну страницу
            vacancies = await self.search_by_keyword(keyword, page=current_page)

            if not vacancies:
                break

            all_vacancies.extend(vacancies)
            current_page += 1

            # Если получили меньше, чем per_page — это последняя страница
            if len(vacancies) < self.per_page:
                break

        logger.info(f"Всего получено {len(all_vacancies)} вакансий с {current_page} страниц")
        return all_vacancies


    def _parse_datetime(self, value: str | None) -> datetime:
        """
        Парсит дату из формата HH.ru в datetime.
        Формат: "2026-06-09T15:41:51+0300"
        Args:
            value: Строка с датой от HH.ru
        Returns:
            datetime: Объект datetime (с часовым поясом или без)
        """
        if not value:
            return datetime.now(timezone.utc)

        try:
            normalized = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", value)
            print(normalized)
            return datetime.fromisoformat(normalized)
        except ValueError as e:
            logger.warning(f"Не удалось распарсить дату '{value}': {e}")
            return datetime.now(timezone.utc)


    def _parse_vacancy(self, raw: dict[str, Any]) -> Vacancy:
        """
        Преобразует сырой JSON от HH.ru в доменную сущность Vacancy.
        Args:
            raw: Словарь с данными вакансии от API
        Returns:
            Vacancy: Доменная сущность
        """
        # Базовые поля (обязательные)
        external_id = raw.get("id", "")
        name = raw.get("name", "Без названия")

        # Работодатель
        employer = raw.get("employer", {})
        employer_name = employer.get("name", "Неизвестный работодатель")

        # Зарплата
        salary = raw.get("salary")
        salary_from = None
        salary_to = None
        currency = "RUR"
        gross = True

        if salary:
            salary_from = salary.get("from")
            salary_to = salary.get("to")
            currency = salary.get("currency", "RUR")
            gross = salary.get("gross", True)

        # Город
        address = raw.get("address")
        city = address.get("city") if address else None

        # Опыт
        experience = raw.get("experience", {})
        experience_id = experience.get("id")
        experience_name = experience.get("name")

        # Описание
        snippet = raw.get("snippet", {})
        requirement = snippet.get("requirement", "")
        responsibility = snippet.get("responsibility", "")

        # Дата публикации
        published_at = self._parse_datetime(raw.get("published_at"))

        # URL
        alternate_url = raw.get("alternate_url", "")

        # Формат работы (из work_format берём первый)
        work_formats = raw.get("work_format", [])
        work_format = "ON_SITE"
        if work_formats and len(work_formats) > 0:
            work_format_id = work_formats[0].get("id", "ON_SITE")
            # Преобразуем в наш внутренний формат
            work_format = work_format_id if work_format_id in ["REMOTE", "MIXED"] else "ON_SITE"

        # Регион
        area = raw.get("area", {})
        area_id = area.get("id")

        # ID работодателя
        employer_id = employer.get("id")

        return Vacancy(
            external_id=external_id,
            name=name,
            employer_id=employer_id,
            employer_name=employer_name,
            requirement=requirement,
            responsibility=responsibility,
            published_at=published_at,
            url=alternate_url,
            alternate_url=alternate_url,
            salary_from=salary_from,
            salary_to=salary_to,
            currency=currency,
            gross=gross,
            city=city,
            area_id=area_id,
            experience_id=experience_id,
            experience_name=experience_name,
            work_format=work_format,
        )
