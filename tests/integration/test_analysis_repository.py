"""Интеграционные тесты для AnalysisRepository."""
import pytest

from shared.domain.entities.analysis import AnalysisStatus
from shared.infrastructure.repositories import (
    PostgresAnalysisRepository,
    PostgresVacancyRepository,
    PostgresResumeRepository,
)
from tests.fixtures.entities.factories import (
    VacancyFactory,
    ResumeFactory,
    AnalysisFactory,
    TestDataFactory,
)


@pytest.mark.asyncio
async def test_save_creates_analysis(test_session):
    """Тест: сохранение нового анализа."""
    vacancy_repo = PostgresVacancyRepository(test_session)
    vacancy = VacancyFactory.create()
    await vacancy_repo.save_batch([vacancy])

    resume_repo = PostgresResumeRepository(test_session)
    resume = ResumeFactory.create()
    saved_resume = await resume_repo.save(resume)

    analysis_repo = PostgresAnalysisRepository(test_session)
    analysis = AnalysisFactory.create(
        vacancy_id=vacancy.external_id,
        resume_id=saved_resume.id,
    )

    saved = await analysis_repo.save(analysis)

    assert saved.id is not None
    assert saved.vacancy_id == vacancy.external_id
    assert saved.resume_id == saved_resume.id
    assert saved.match_score == 85.5
    assert saved.strengths == ["Python", "Docker"]
    assert saved.weaknesses == ["No SQL"]
    assert saved.status == AnalysisStatus.COMPLETED


@pytest.mark.asyncio
async def test_save_updates_analysis(test_session):
    """Тест: обновление существующего анализа."""
    data = await TestDataFactory.save_full_analysis_set(
        session=test_session,
        analysis_kwargs={"match_score": 70.0, "strengths": ["Python"]},
    )
    analysis = data["analysis"]

    analysis.match_score = 90.0
    analysis.strengths.append("Docker")
    analysis.weaknesses = ["Kubernetes"]
    analysis.status = AnalysisStatus.COMPLETED

    analysis_repo = PostgresAnalysisRepository(test_session)
    updated = await analysis_repo.save(analysis)

    assert updated.id == analysis.id
    assert updated.match_score == 90.0
    assert "Docker" in updated.strengths
    assert "Kubernetes" in updated.weaknesses
    assert updated.status == AnalysisStatus.COMPLETED


@pytest.mark.asyncio
async def test_get_by_id_found(test_session):
    """Тест: получение существующего анализа."""
    data = await TestDataFactory.save_full_analysis_set(session=test_session)
    analysis = data["analysis"]

    analysis_repo = PostgresAnalysisRepository(test_session)

    result = await analysis_repo.get_by_id(analysis.id)

    assert result is not None
    assert result.id == analysis.id
    assert result.vacancy_id == analysis.vacancy_id
    assert result.resume_id == analysis.resume_id
    assert result.match_score == analysis.match_score


@pytest.mark.asyncio
async def test_get_by_id_not_found(test_session):
    """Тест: получение несуществующего анализа."""
    analysis_repo = PostgresAnalysisRepository(test_session)

    result = await analysis_repo.get_by_id(999)

    assert result is None


@pytest.mark.asyncio
async def test_get_by_vacancy_and_resume(test_session):
    """Тест: получение анализа по вакансии и резюме."""
    data = await TestDataFactory.save_full_analysis_set(session=test_session)
    analysis = data["analysis"]
    vacancy = data["vacancy"]
    resume = data["resume"]

    analysis_repo = PostgresAnalysisRepository(test_session)

    result = await analysis_repo.get_by_vacancy_and_resume(
        vacancy_id=vacancy.external_id,
        resume_id=resume.id,
    )

    assert result is not None
    assert result.id == analysis.id
    assert result.vacancy_id == vacancy.external_id
    assert result.resume_id == resume.id


@pytest.mark.asyncio
async def test_get_pending(test_session):
    """Тест: получение анализов со статусом PENDING."""
    vacancy_repo = PostgresVacancyRepository(test_session)
    vacancy = VacancyFactory.create()
    await vacancy_repo.save_batch([vacancy])

    resume_repo = PostgresResumeRepository(test_session)
    resume = ResumeFactory.create()
    saved_resume = await resume_repo.save(resume)

    analysis_repo = PostgresAnalysisRepository(test_session)

    pending1 = AnalysisFactory.create_pending(
        vacancy_id=vacancy.external_id,
        resume_id=saved_resume.id,
    )
    pending2 = AnalysisFactory.create_pending(
        vacancy_id=vacancy.external_id,
        resume_id=saved_resume.id,
    )
    completed = AnalysisFactory.create(
        vacancy_id=vacancy.external_id,
        resume_id=saved_resume.id,
    )

    await analysis_repo.save(pending1)
    await analysis_repo.save(pending2)
    await analysis_repo.save(completed)

    results = await analysis_repo.get_pending(limit=10)

    assert len(results) >= 2
    assert all(r.status == AnalysisStatus.PENDING for r in results)


@pytest.mark.asyncio
async def test_get_by_status(test_session):
    """Тест: получение анализов по статусу."""
    vacancy_repo = PostgresVacancyRepository(test_session)
    vacancy = VacancyFactory.create()
    await vacancy_repo.save_batch([vacancy])

    resume_repo = PostgresResumeRepository(test_session)
    resume = ResumeFactory.create()
    saved_resume = await resume_repo.save(resume)

    analysis_repo = PostgresAnalysisRepository(test_session)

    pending = AnalysisFactory.create_pending(
        vacancy_id=vacancy.external_id,
        resume_id=saved_resume.id,
    )
    failed = AnalysisFactory.create(
        vacancy_id=vacancy.external_id,
        resume_id=saved_resume.id,
        status=AnalysisStatus.FAILED,
        error_message="Ошибка LLM",
    )

    await analysis_repo.save(pending)
    await analysis_repo.save(failed)

    pending_results = await analysis_repo.get_by_status(AnalysisStatus.PENDING)
    failed_results = await analysis_repo.get_by_status(AnalysisStatus.FAILED)

    assert len(pending_results) >= 1
    assert all(r.status == AnalysisStatus.PENDING for r in pending_results)
    assert len(failed_results) >= 1
    assert all(r.status == AnalysisStatus.FAILED for r in failed_results)


@pytest.mark.asyncio
async def test_update_status(test_session):
    """Тест: обновление статуса анализа."""
    data = await TestDataFactory.save_full_analysis_set(
        session=test_session,
        analysis_kwargs={"status": AnalysisStatus.PENDING},
    )
    analysis = data["analysis"]

    analysis_repo = PostgresAnalysisRepository(test_session)

    updated = await analysis_repo.update_status(analysis.id, AnalysisStatus.COMPLETED)

    assert updated is not None
    assert updated.id == analysis.id
    assert updated.status == AnalysisStatus.COMPLETED


@pytest.mark.asyncio
async def test_update_status_not_found(test_session):
    """Тест: обновление статуса несуществующего анализа."""
    analysis_repo = PostgresAnalysisRepository(test_session)

    # Act
    result = await analysis_repo.update_status(999, AnalysisStatus.COMPLETED)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_save_with_mark_completed(test_session):
    """Тест: сохранение анализа с использованием метода mark_completed."""
    vacancy_repo = PostgresVacancyRepository(test_session)
    vacancy = VacancyFactory.create()
    await vacancy_repo.save_batch([vacancy])

    resume_repo = PostgresResumeRepository(test_session)
    resume = ResumeFactory.create()
    saved_resume = await resume_repo.save(resume)

    analysis = AnalysisFactory.create_pending(
        vacancy_id=vacancy.external_id,
        resume_id=saved_resume.id,
    )
    analysis.mark_completed(
        score=95.0,
        strengths=["Python", "Docker"],
        weaknesses=["No SQL"],
    )

    analysis_repo = PostgresAnalysisRepository(test_session)
    saved = await analysis_repo.save(analysis)

    assert saved.id is not None
    assert saved.match_score == 95.0
    assert saved.strengths == ["Python", "Docker"]
    assert saved.weaknesses == ["No SQL"]
    assert saved.status == AnalysisStatus.COMPLETED
    assert saved.completed_at is not None


@pytest.mark.asyncio
async def test_save_with_mark_failed(test_session):
    """Тест: сохранение анализа с использованием метода mark_failed."""
    vacancy_repo = PostgresVacancyRepository(test_session)
    vacancy = VacancyFactory.create()
    await vacancy_repo.save_batch([vacancy])

    resume_repo = PostgresResumeRepository(test_session)
    resume = ResumeFactory.create()
    saved_resume = await resume_repo.save(resume)

    analysis = AnalysisFactory.create_pending(
        vacancy_id=vacancy.external_id,
        resume_id=saved_resume.id,
    )
    analysis.mark_failed("Ошибка LLM: превышен таймаут")

    analysis_repo = PostgresAnalysisRepository(test_session)
    saved = await analysis_repo.save(analysis)

    assert saved.id is not None
    assert saved.status == AnalysisStatus.FAILED
    assert saved.error_message == "Ошибка LLM: превышен таймаут"
    assert saved.retry_count == 1


@pytest.mark.asyncio
async def test_save_with_mark_in_progress(test_session):
    """Тест: сохранение анализа с использованием метода mark_in_progress."""
    vacancy_repo = PostgresVacancyRepository(test_session)
    vacancy = VacancyFactory.create()
    await vacancy_repo.save_batch([vacancy])

    resume_repo = PostgresResumeRepository(test_session)
    resume = ResumeFactory.create()
    saved_resume = await resume_repo.save(resume)

    analysis = AnalysisFactory.create_pending(
        vacancy_id=vacancy.external_id,
        resume_id=saved_resume.id,
    )
    analysis.mark_in_progress()

    analysis_repo = PostgresAnalysisRepository(test_session)
    saved = await analysis_repo.save(analysis)

    assert saved.id is not None
    assert saved.status == AnalysisStatus.IN_PROGRESS
