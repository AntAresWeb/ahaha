"""Интеграционные тесты для VacancyReplyRepository."""
import pytest

from shared.domain.entities.vacancy_reply import VacancyReplyStatus
from shared.infrastructure.repositories import (
    PostgresVacancyReplyRepository,
    PostgresVacancyRepository,
    PostgresResumeRepository,
    PostgresAnalysisRepository,
)
from tests.fixtures.entities.factories import (
    VacancyFactory,
    ResumeFactory,
    AnalysisFactory,
    VacancyReplyFactory,
    TestDataFactory,
)


# ============================================================
# Базовые тесты CRUD
# ============================================================

@pytest.mark.asyncio
async def test_save_creates_reply(test_session):
    """Тест: сохранение нового отклика."""
    # 1. Сохраняем вакансию
    vacancy_repo = PostgresVacancyRepository(test_session)
    vacancy = VacancyFactory.create()
    await vacancy_repo.save_batch([vacancy])

    # 2. Сохраняем резюме
    resume_repo = PostgresResumeRepository(test_session)
    resume = ResumeFactory.create()
    saved_resume = await resume_repo.save(resume)

    # 3. Сохраняем анализ
    analysis_repo = PostgresAnalysisRepository(test_session)
    analysis = AnalysisFactory.create(
        vacancy_id=vacancy.external_id,
        resume_id=saved_resume.id,
    )
    saved_analysis = await analysis_repo.save(analysis)

    # 4. Создаем отклик
    reply_repo = PostgresVacancyReplyRepository(test_session)
    reply = VacancyReplyFactory.create(
        vacancy_id=vacancy.external_id,
        resume_id=saved_resume.id,
        analysis_id=saved_analysis.id,
    )

    # Act
    saved = await reply_repo.save(reply)

    # Assert
    assert saved.id is not None
    assert saved.vacancy_id == vacancy.external_id
    assert saved.resume_id == saved_resume.id
    assert saved.analysis_id == saved_analysis.id
    assert saved.cover_letter == "Здравствуйте! Заинтересовался вашей вакансией..."
    assert saved.match_score == 85.5
    assert saved.status == VacancyReplyStatus.READY


@pytest.mark.asyncio
async def test_save_updates_reply(test_session):
    """Тест: обновление существующего отклика."""
    # ✅ Создаем и сохраняем все зависимости
    data = await TestDataFactory.save_full_reply_set(
        session=test_session,
        reply_kwargs={"cover_letter": "Оригинальный текст", "match_score": 85.0},
    )
    reply = data["reply"]

    # ✅ Обновляем отклик
    reply.cover_letter = "Обновленный текст"
    reply.match_score = 95.0
    reply.status = VacancyReplyStatus.SENT

    reply_repo = PostgresVacancyReplyRepository(test_session)
    updated = await reply_repo.save(reply)

    # Assert
    assert updated.id == reply.id
    assert updated.cover_letter == "Обновленный текст"
    assert updated.match_score == 95.0
    assert updated.status == VacancyReplyStatus.SENT


@pytest.mark.asyncio
async def test_get_by_id_found(test_session):
    """Тест: получение существующего отклика."""
    # ✅ Создаем и сохраняем отклик
    data = await TestDataFactory.save_full_reply_set(session=test_session)
    reply = data["reply"]

    reply_repo = PostgresVacancyReplyRepository(test_session)

    # Act
    result = await reply_repo.get_by_id(reply.id)

    # Assert
    assert result is not None
    assert result.id == reply.id
    assert result.vacancy_id == reply.vacancy_id
    assert result.resume_id == reply.resume_id
    assert result.analysis_id == reply.analysis_id


@pytest.mark.asyncio
async def test_get_by_id_not_found(test_session):
    """Тест: получение несуществующего отклика."""
    reply_repo = PostgresVacancyReplyRepository(test_session)

    # Act
    result = await reply_repo.get_by_id(999)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_get_by_vacancy_and_resume(test_session):
    """Тест: получение отклика по вакансии и резюме."""
    # ✅ Создаем и сохраняем отклик
    data = await TestDataFactory.save_full_reply_set(session=test_session)
    reply = data["reply"]
    vacancy = data["vacancy"]
    resume = data["resume"]

    reply_repo = PostgresVacancyReplyRepository(test_session)

    # Act
    result = await reply_repo.get_by_vacancy_and_resume(
        vacancy_id=vacancy.external_id,
        resume_id=resume.id,
    )

    # Assert
    assert result is not None
    assert result.id == reply.id
    assert result.vacancy_id == vacancy.external_id
    assert result.resume_id == resume.id


# ============================================================
# Тесты фильтрации по статусам
# ============================================================

@pytest.mark.asyncio
async def test_get_by_status(test_session):
    """Тест: получение откликов по статусу."""
    # ✅ Создаем вакансию и резюме
    vacancy_repo = PostgresVacancyRepository(test_session)
    vacancy = VacancyFactory.create()
    await vacancy_repo.save_batch([vacancy])

    resume_repo = PostgresResumeRepository(test_session)
    resume = ResumeFactory.create()
    saved_resume = await resume_repo.save(resume)

    # ✅ Создаем анализы и отклики
    analysis_repo = PostgresAnalysisRepository(test_session)
    reply_repo = PostgresVacancyReplyRepository(test_session)

    for i in range(3):
        analysis = AnalysisFactory.create(
            vacancy_id=vacancy.external_id,
            resume_id=saved_resume.id,
        )
        saved_analysis = await analysis_repo.save(analysis)

        reply = VacancyReplyFactory.create(
            vacancy_id=vacancy.external_id,
            resume_id=saved_resume.id,
            analysis_id=saved_analysis.id,
            status=VacancyReplyStatus.READY if i % 2 == 0 else VacancyReplyStatus.SENT,
        )
        await reply_repo.save(reply)

    # Act
    ready_results = await reply_repo.get_by_status(VacancyReplyStatus.READY)
    sent_results = await reply_repo.get_by_status(VacancyReplyStatus.SENT)

    # Assert
    assert len(ready_results) >= 1
    assert all(r.status == VacancyReplyStatus.READY for r in ready_results)
    assert len(sent_results) >= 1
    assert all(r.status == VacancyReplyStatus.SENT for r in sent_results)


@pytest.mark.asyncio
async def test_get_ready_to_send(test_session):
    """Тест: получение откликов, готовых к отправке."""
    # ✅ Создаем вакансию и резюме
    vacancy_repo = PostgresVacancyRepository(test_session)
    vacancy = VacancyFactory.create()
    await vacancy_repo.save_batch([vacancy])

    resume_repo = PostgresResumeRepository(test_session)
    resume = ResumeFactory.create()
    saved_resume = await resume_repo.save(resume)

    # ✅ Создаем анализы и отклики
    analysis_repo = PostgresAnalysisRepository(test_session)
    reply_repo = PostgresVacancyReplyRepository(test_session)

    # Создаем READY отклики
    for i in range(2):
        analysis = AnalysisFactory.create(
            vacancy_id=vacancy.external_id,
            resume_id=saved_resume.id,
        )
        saved_analysis = await analysis_repo.save(analysis)

        reply = VacancyReplyFactory.create_ready(
            vacancy_id=vacancy.external_id,
            resume_id=saved_resume.id,
            analysis_id=saved_analysis.id,
        )
        await reply_repo.save(reply)

    # Создаем SENT отклик
    analysis = AnalysisFactory.create(
        vacancy_id=vacancy.external_id,
        resume_id=saved_resume.id,
    )
    saved_analysis = await analysis_repo.save(analysis)
    sent_reply = VacancyReplyFactory.create(
        vacancy_id=vacancy.external_id,
        resume_id=saved_resume.id,
        analysis_id=saved_analysis.id,
        status=VacancyReplyStatus.SENT,
    )
    await reply_repo.save(sent_reply)

    # Act
    results = await reply_repo.get_ready_to_send(limit=10)

    # Assert
    assert len(results) >= 2
    assert all(r.status == VacancyReplyStatus.READY for r in results)


@pytest.mark.asyncio
async def test_update_status(test_session):
    """Тест: обновление статуса отклика."""
    # ✅ Создаем и сохраняем отклик
    data = await TestDataFactory.save_full_reply_set(
        session=test_session,
        reply_kwargs={"status": VacancyReplyStatus.READY},
    )
    reply = data["reply"]

    reply_repo = PostgresVacancyReplyRepository(test_session)

    # Act
    updated = await reply_repo.update_status(reply.id, VacancyReplyStatus.SENT)

    # Assert
    assert updated is not None
    assert updated.id == reply.id
    assert updated.status == VacancyReplyStatus.SENT


@pytest.mark.asyncio
async def test_exists_for_vacancy_true(test_session):
    """Тест: проверка существования отклика для вакансии (существует)."""
    # ✅ Создаем и сохраняем отклик
    data = await TestDataFactory.save_full_reply_set(session=test_session)
    vacancy = data["vacancy"]

    reply_repo = PostgresVacancyReplyRepository(test_session)

    # Act
    result = await reply_repo.exists_for_vacancy(vacancy.external_id)

    # Assert
    assert result is True


@pytest.mark.asyncio
async def test_exists_for_vacancy_false(test_session):
    """Тест: проверка существования отклика для вакансии (не существует)."""
    reply_repo = PostgresVacancyReplyRepository(test_session)

    # Act
    result = await reply_repo.exists_for_vacancy("non_existent")

    # Assert
    assert result is False


# ============================================================
# Тесты с методами mark_*
# ============================================================

@pytest.mark.asyncio
async def test_save_with_mark_ready(test_session):
    """Тест: сохранение отклика с использованием метода mark_ready."""
    # ✅ Создаем вакансию, резюме и анализ
    data = await TestDataFactory.save_full_analysis_set(session=test_session)
    vacancy = data["vacancy"]
    resume = data["resume"]
    analysis = data["analysis"]

    # ✅ Создаем отклик и отмечаем как READY
    reply = VacancyReplyFactory.create(
        vacancy_id=vacancy.external_id,
        resume_id=resume.id,
        analysis_id=analysis.id,
        status=VacancyReplyStatus.PENDING,
    )
    reply.mark_ready()

    reply_repo = PostgresVacancyReplyRepository(test_session)
    saved = await reply_repo.save(reply)

    # Assert
    assert saved.id is not None
    assert saved.status == VacancyReplyStatus.READY


@pytest.mark.asyncio
async def test_save_with_mark_sent(test_session):
    """Тест: сохранение отклика с использованием метода mark_sent."""
    # ✅ Создаем вакансию, резюме и анализ
    data = await TestDataFactory.save_full_analysis_set(session=test_session)
    vacancy = data["vacancy"]
    resume = data["resume"]
    analysis = data["analysis"]

    # ✅ Создаем отклик и отмечаем как SENT
    reply = VacancyReplyFactory.create(
        vacancy_id=vacancy.external_id,
        resume_id=resume.id,
        analysis_id=analysis.id,
        status=VacancyReplyStatus.READY,
    )
    reply.mark_sent("hh_message_123")

    reply_repo = PostgresVacancyReplyRepository(test_session)
    saved = await reply_repo.save(reply)

    # Assert
    assert saved.id is not None
    assert saved.status == VacancyReplyStatus.SENT
    assert saved.message_id == "hh_message_123"
    assert saved.sent_at is not None


@pytest.mark.asyncio
async def test_save_with_mark_failed(test_session):
    """Тест: сохранение отклика с использованием метода mark_failed."""
    # ✅ Создаем вакансию, резюме и анализ
    data = await TestDataFactory.save_full_analysis_set(session=test_session)
    vacancy = data["vacancy"]
    resume = data["resume"]
    analysis = data["analysis"]

    # ✅ Создаем отклик и отмечаем как FAILED
    reply = VacancyReplyFactory.create(
        vacancy_id=vacancy.external_id,
        resume_id=resume.id,
        analysis_id=analysis.id,
        status=VacancyReplyStatus.READY,
    )
    reply.mark_failed("Ошибка отправки в HH")

    reply_repo = PostgresVacancyReplyRepository(test_session)
    saved = await reply_repo.save(reply)

    # Assert
    assert saved.id is not None
    assert saved.status == VacancyReplyStatus.FAILED
    assert saved.error_message == "Ошибка отправки в HH"
    assert saved.retry_count == 1


@pytest.mark.asyncio
async def test_save_with_mark_rejected(test_session):
    """Тест: сохранение отклика с использованием метода mark_rejected."""
    # ✅ Создаем вакансию, резюме и анализ
    data = await TestDataFactory.save_full_analysis_set(session=test_session)
    vacancy = data["vacancy"]
    resume = data["resume"]
    analysis = data["analysis"]

    # ✅ Создаем отклик и отмечаем как REJECTED
    reply = VacancyReplyFactory.create(
        vacancy_id=vacancy.external_id,
        resume_id=resume.id,
        analysis_id=analysis.id,
        status=VacancyReplyStatus.PENDING,
    )
    reply.mark_rejected("Вакансия закрыта")

    reply_repo = PostgresVacancyReplyRepository(test_session)
    saved = await reply_repo.save(reply)

    # Assert
    assert saved.id is not None
    assert saved.status == VacancyReplyStatus.REJECTED
    assert saved.error_message == "Вакансия закрыта"
