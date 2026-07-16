from datetime import datetime, timezone
from typing import Any

from src.vacancy_analizer.domain.entities.vacancy import Vacancy
from src.vacancy_analizer.infrastructure.db.models.vacancy import VacancyORM


def vacancy_to_orm(vacancy: Vacancy) -> VacancyORM:
    """Преобразует доменную сущность в ORM-модель."""
    return VacancyORM(
        external_id=vacancy.external_id,
        name=vacancy.name,
        employer_name=vacancy.employer_name,
        requirement=vacancy.requirement or "",
        responsibility=vacancy.responsibility or "",
        published_at=vacancy.published_at,
        url=vacancy.url or "",
        alternate_url=vacancy.alternate_url or "",
        salary_from=vacancy.salary_from,
        salary_to=vacancy.salary_to,
        currency=vacancy.currency or "RUR",
        gross=vacancy.gross,
        city=vacancy.city,
        area_id=vacancy.area_id,
        experience_id=vacancy.experience_id,
        experience_name=vacancy.experience_name,
        work_format=vacancy.work_format or "ON_SITE",
        employer_id=vacancy.employer_id,
        company_logo_url=vacancy.company_logo_url,
    )


def orm_to_vacancy(orm: VacancyORM) -> Vacancy:
    """Преобразует ORM-модель в доменную сущность."""
    return Vacancy(
        external_id=orm.external_id,
        name=orm.name,
        employer_name=orm.employer_name,
        requirement=orm.requirement,
        responsibility=orm.responsibility,
        published_at=orm.published_at,
        url=orm.url,
        alternate_url=orm.alternate_url,
        salary_from=orm.salary_from,
        salary_to=orm.salary_to,
        currency=orm.currency,
        gross=orm.gross,
        city=orm.city,
        area_id=orm.area_id,
        experience_id=orm.experience_id,
        experience_name=orm.experience_name,
        work_format=orm.work_format,
        employer_id=orm.employer_id,
        company_logo_url=orm.company_logo_url,
    )

def vacancy_to_orm_dict(vacancy: Vacancy) -> dict[str, Any]:
    """Преобразует доменную сущность в словарь для ORM."""
    return {
        "external_id": vacancy.external_id,
        "name": vacancy.name,
        "employer_name": vacancy.employer_name,
        "salary_from": vacancy.salary_from,
        "salary_to": vacancy.salary_to,
        "currency": vacancy.currency,
        "gross": vacancy.gross,
        "city": vacancy.city,
        "area_id": vacancy.area_id,
        "experience_id": vacancy.experience_id,
        "experience_name": vacancy.experience_name,
        "requirement": vacancy.requirement,
        "responsibility": vacancy.responsibility,
        "published_at": vacancy.published_at,
        "url": vacancy.url,
        "alternate_url": vacancy.alternate_url,
        "work_format": vacancy.work_format,
        "employer_id": vacancy.employer_id,
        "company_logo_url": vacancy.company_logo_url,
        "updated_at": datetime.now(timezone.utc),
    }
