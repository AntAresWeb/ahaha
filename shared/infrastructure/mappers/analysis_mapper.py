from typing import Any

from shared.domain.entities.analysis import Analysis, AnalysisStatus
from shared.infrastructure.models.analysis import AnalysisORM


def analysis_to_orm(analysis: Analysis) -> AnalysisORM:
    """Преобразует доменную сущность в ORM-модель."""
    return AnalysisORM(**analysis_to_orm_dict(analysis))


def orm_to_analysis(orm: AnalysisORM) -> Analysis:
    """Преобразует ORM-модель в доменную сущность Analysis."""
    return Analysis(
        id=orm.id,
        vacancy_id=orm.vacancy_id,
        resume_id=orm.resume_id,
        match_score=orm.match_score,
        strengths=orm.strengths.split(",") if orm.strengths else [],
        weaknesses=orm.weaknesses.split(",") if orm.weaknesses else [],
        analysis_details=orm.analysis_details,
        status=AnalysisStatus(orm.status),
        error_message=orm.error_message,
        retry_count=orm.retry_count,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
        completed_at=orm.completed_at,
    )


def analysis_to_orm_dict(analysis: Analysis) -> dict[str, Any]:
    """Преобразует доменную сущность в словарь для ORM."""
    data = {
        "resume_id": analysis.resume_id,
        "vacancy_id": analysis.vacancy_id,
        "match_score": float(analysis.match_score) if analysis.match_score is not None else None,
        "strengths": ",".join(analysis.strengths) if analysis.strengths else "[]",
        "weaknesses": ",".join(analysis.weaknesses) if analysis.weaknesses else "[]",
        "analysis_details": analysis.analysis_details,
        "status": analysis.status.value,
        "error_message": analysis.error_message,
        "retry_count": analysis.retry_count,
    }

    if analysis.id:
        data["id"] = analysis.id
    return data
