from datetime import datetime, timezone
from typing import Any

from shared.domain.entities.resume import Resume
from shared.infrastructure.models.resume import ResumeORM


def resume_to_orm(resume: Resume) -> ResumeORM:
    """Преобразует доменную сущность Resume в ORM-модель."""
    return ResumeORM(
        id=resume.id,
        hh_resume_id=resume.hh_resume_id,
        profession=resume.profession,
        skills=",".join(resume.skills) if resume.skills else "",
        full_text=resume.full_text,
        is_active=resume.is_active,
    )


def orm_to_resume(orm: ResumeORM) -> Resume:
    """Преобразует ORM-модель в доменную сущность Resume."""
    return Resume(
        id=orm.id,
        hh_resume_id=orm.hh_resume_id,
        profession=orm.profession,
        skills=orm.skills.split(",") if orm.skills else [],
        full_text=orm.full_text,
        is_active=orm.is_active,
        created_at=orm.created_at,
    )


def resume_to_orm_dict(resume: Resume) -> dict[str, Any]:
    """Преобразует доменную сущность в словарь для ORM."""
    return {
        "id": resume.id,
        "hh_resume_id": resume.hh_resume_id,
        "profession": resume.profession,
        "skills": ",".join(resume.skills) if resume.skills else "",
        "full_text": resume.full_text,
        "is_active": resume.is_active,
        "updated_at": datetime.now(timezone.utc),
    }
