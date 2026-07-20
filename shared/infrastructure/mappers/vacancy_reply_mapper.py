from datetime import datetime, timezone
from typing import Any

from shared.domain.entities.vacancy_reply import VacancyReply, VacancyReplyStatus
from shared.infrastructure.models.vacancy_reply import VacancyReplyORM


def vacancy_reply_to_orm(reply: VacancyReply) -> VacancyReplyORM:
    """Преобразует доменную сущность VacancyReply в ORM-модель."""
    return VacancyReplyORM(
        id=reply.id,
        vacancy_id=reply.vacancy_id,
        resume_id=reply.resume_id,
        analysis_id=reply.analysis_id,
        cover_letter=reply.cover_letter,
        match_score=reply.match_score,
        status=reply.status.value,
        error_message=reply.error_message,
        message_id=reply.message_id,
        retry_count=reply.retry_count,
        sent_at=reply.sent_at,
    )


def orm_to_vacancy_reply(orm: VacancyReplyORM) -> VacancyReply:
    """Преобразует ORM-модель в доменную сущность VacancyReply."""
    return VacancyReply(
        id=orm.id,
        vacancy_id=orm.vacancy_id,
        resume_id=orm.resume_id,
        analysis_id=orm.analysis_id,
        cover_letter=orm.cover_letter,
        match_score=orm.match_score,
        status=VacancyReplyStatus(orm.status),
        error_message=orm.error_message,
        message_id=orm.message_id,
        retry_count=orm.retry_count,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
        sent_at=orm.sent_at,
    )


def vacancy_reply_to_orm_dict(reply: VacancyReply) -> dict[str, Any]:
    """Преобразует доменную сущность в словарь для ORM."""
    return {
        "id": reply.id,
        "vacancy_id": reply.vacancy_id,
        "resume_id": reply.resume_id,
        "analysis_id": reply.analysis_id,
        "cover_letter": reply.cover_letter,
        "match_score": reply.match_score,
        "status": reply.status.value,
        "error_message": reply.error_message,
        "message_id": reply.message_id,
        "retry_count": reply.retry_count,
        "sent_at": reply.sent_at,
        "updated_at": datetime.now(timezone.utc),
    }
