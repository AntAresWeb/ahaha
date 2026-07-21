"""Интеграционные тесты для VacancyReplyRepository."""
import pytest

from shared.domain.entities.vacancy_reply import VacancyReplyStatus
from shared.infrastructure.repositories.vacancy_reply_repository import PostgresVacancyReplyRepository
from tests.fixtures.entities.factories import VacancyReplyFactory


@pytest.mark.asyncio
async def test_save_creates_reply(test_session):
    """Тест: сохранение нового отклика."""
    repo = PostgresVacancyReplyRepository(test_session)
    reply = VacancyReplyFactory.create()
    assert reply.id is None
    
    # Act
    saved = await repo.save(reply)
    
    # Assert
    assert saved.id is not None
    assert saved.vacancy_id == reply.vacancy_id
    assert saved.resume_id == reply.resume_id
    assert saved.cover_letter == reply.cover_letter


@pytest.mark.asyncio
async def test_save_updates_reply(test_session):
    """Тест: обновление существующего отклика."""
    repo = PostgresVacancyReplyRepository(test_session)
    
    # Создаем новый отклик
    reply = VacancyReplyFactory.create(
        vacancy_id=1,
        resume_id=1,
        cover_letter="Оригинальный текст",
        match_score=85.0
    )
    # Сохраняем — получаем id
    saved = await repo.save(reply)
    
    # Теперь меняем поля
    saved.cover_letter = "Обновленный текст"
    saved.match_score = 95.0
    
    # Сохраняем снова — должно обновить
    updated = await repo.save(saved)
    
    # Проверяем
    assert updated.id == saved.id
    assert updated.cover_letter == "Обновленный текст"
    assert updated.match_score == 95.0


@pytest.mark.asyncio
async def test_get_by_id_found(test_session):
    """Тест: получение существующего отклика."""
    repo = PostgresVacancyReplyRepository(test_session)
    reply = VacancyReplyFactory.create()
    saved = await repo.save(reply)
    
    # Act
    result = await repo.get_by_id(saved.id)
    
    # Assert
    assert result is not None
    assert result.id == saved.id
    assert result.vacancy_id == reply.vacancy_id
    assert result.resume_id == reply.resume_id


@pytest.mark.asyncio
async def test_get_by_id_not_found(test_session):
    """Тест: получение несуществующего отклика."""
    repo = PostgresVacancyReplyRepository(test_session)
    
    # Act
    result = await repo.get_by_id(999)
    
    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_get_by_vacancy_and_resume(test_session):
    """Тест: получение отклика по вакансии и резюме."""
    repo = PostgresVacancyReplyRepository(test_session)
    reply = VacancyReplyFactory.create(vacancy_id="10", resume_id=20)
    await repo.save(reply)
    
    # Act
    result = await repo.get_by_vacancy_and_resume("10", 20)
    
    # Assert
    assert result is not None
    assert result.vacancy_id == "10"
    assert result.resume_id == 20


@pytest.mark.asyncio
async def test_get_by_status(test_session):
    """Тест: получение откликов по статусу."""
    repo = PostgresVacancyReplyRepository(test_session)
    
    ready = VacancyReplyFactory.create_ready()
    sent = VacancyReplyFactory.create_sent()
    
    await repo.save(ready)
    await repo.save(sent)
    
    # Act
    ready_results = await repo.get_by_status(VacancyReplyStatus.READY)
    sent_results = await repo.get_by_status(VacancyReplyStatus.SENT)
    
    # Assert
    assert len(ready_results) == 1
    assert ready_results[0].status == VacancyReplyStatus.READY
    assert len(sent_results) == 1
    assert sent_results[0].status == VacancyReplyStatus.SENT


@pytest.mark.asyncio
async def test_get_ready_to_send(test_session):
    """Тест: получение откликов, готовых к отправке."""
    repo = PostgresVacancyReplyRepository(test_session)
    
    ready1 = VacancyReplyFactory.create_ready()
    ready2 = VacancyReplyFactory.create_ready()
    sent = VacancyReplyFactory.create_sent()
    
    await repo.save(ready1)
    await repo.save(ready2)
    await repo.save(sent)
    
    # Act
    results = await repo.get_ready_to_send(limit=10)
    
    # Assert
    assert len(results) == 2
    assert all(r.status == VacancyReplyStatus.READY for r in results)


@pytest.mark.asyncio
async def test_update_status(test_session):
    """Тест: обновление статуса отклика."""
    repo = PostgresVacancyReplyRepository(test_session)
    reply = VacancyReplyFactory.create()
    saved = await repo.save(reply)
    
    # Act
    updated = await repo.update_status(saved.id, VacancyReplyStatus.SENT)
    
    # Assert
    assert updated is not None
    assert updated.id == saved.id
    assert updated.status == VacancyReplyStatus.SENT


@pytest.mark.asyncio
async def test_exists_for_vacancy_true(test_session):
    """Тест: проверка существования отклика для вакансии (существует)."""
    repo = PostgresVacancyReplyRepository(test_session)
    reply = VacancyReplyFactory.create(vacancy_id=5)
    await repo.save(reply)
    
    # Act
    result = await repo.exists_for_vacancy(5)
    
    # Assert
    assert result is True


@pytest.mark.asyncio
async def test_exists_for_vacancy_false(test_session):
    """Тест: проверка существования отклика для вакансии (не существует)."""
    repo = PostgresVacancyReplyRepository(test_session)
    
    # Act
    result = await repo.exists_for_vacancy(999)
    
    # Assert
    assert result is False
