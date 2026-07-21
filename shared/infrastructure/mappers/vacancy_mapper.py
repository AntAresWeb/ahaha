"""Маппер для преобразования между Vacancy и VacancyORM."""
from datetime import datetime, timezone
from typing import Any

from shared.domain.entities.vacancy import Vacancy
from shared.infrastructure.models.vacancy import VacancyORM


def vacancy_to_orm(vacancy: Vacancy) -> VacancyORM:
    """Преобразует доменную сущность в ORM-модель."""
    return VacancyORM(
        external_id=vacancy.external_id,
        url=vacancy.url,
        name=vacancy.name,
        employer_id=vacancy.employer_id,
        employer_name=vacancy.employer_name,
        requirement=vacancy.requirement or "",
        responsibility=vacancy.responsibility or "",
        salary_from=vacancy.salary_from,
        salary_to=vacancy.salary_to,
        city=vacancy.city,
        experience_name=vacancy.experience_name,
        work_format=vacancy.work_format or "REMOTE",
        published_at=vacancy.published_at,
        full_text=vacancy.full_text,
        is_archived=vacancy.is_archived,
    )


def orm_to_vacancy(orm: VacancyORM) -> Vacancy:
    """Преобразует ORM-модель в доменную сущность."""
    return Vacancy(
        external_id=orm.external_id,
        url=orm.url,
        name=orm.name,
        employer_id=orm.employer_id,
        employer_name=orm.employer_name,
        requirement=orm.requirement,
        responsibility=orm.responsibility,
        salary_from=orm.salary_from,
        salary_to=orm.salary_to,
        city=orm.city,
        experience_name=orm.experience_name,
        work_format=orm.work_format,
        published_at=orm.published_at,
        full_text=orm.full_text,
        is_archived=orm.is_archived,
        created_at=orm.created_at,
    )


def vacancy_to_orm_dict(vacancy: Vacancy) -> dict[str, Any]:
    """Преобразует доменную сущность в словарь для ORM (для UPSERT)."""
    return {
        "external_id": vacancy.external_id,
        "url": vacancy.url,
        "name": vacancy.name,
        "employer_id": vacancy.employer_id,
        "employer_name": vacancy.employer_name,
        "requirement": vacancy.requirement or "",
        "responsibility": vacancy.responsibility or "",
        "salary_from": vacancy.salary_from,
        "salary_to": vacancy.salary_to,
        "city": vacancy.city,
        "experience_name": vacancy.experience_name,
        "work_format": vacancy.work_format or "REMOTE",
        "published_at": vacancy.published_at,
        "full_text": vacancy.full_text,
        "is_archived": vacancy.is_archived,
        "updated_at": datetime.now(timezone.utc),  # Для Base.updated_at
    }
