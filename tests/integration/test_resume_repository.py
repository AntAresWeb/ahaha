"""Интеграционные тесты для ResumeRepository."""
import pytest

from shared.infrastructure.repositories.resume_repository import PostgresResumeRepository
from tests.fixtures.entities.factories import ResumeFactory


@pytest.mark.asyncio
async def test_save_creates_resume(test_session):
    """Тест: сохранение нового резюме."""
    repo = PostgresResumeRepository(test_session)
    resume = ResumeFactory.create()
    assert resume.id is None
    
    saved = await repo.save(resume)
    
    assert saved.id is not None
    assert saved.profession == resume.profession
    assert saved.skills == resume.skills
    assert saved.full_text == resume.full_text


@pytest.mark.asyncio
async def test_save_updates_resume(test_session):
    """Тест: обновление существующего резюме."""
    repo = PostgresResumeRepository(test_session)
    resume = ResumeFactory.create(profession="Python Developer")
    
    saved = await repo.save(resume)
    assert saved.profession == "Python Developer"
    
    resume.profession = "Senior Python Developer"
    resume.skills.append("Kubernetes")
    updated = await repo.save(resume)
    
    assert updated.id == saved.id
    assert updated.profession == "Senior Python Developer"
    assert "Kubernetes" in updated.skills


@pytest.mark.asyncio
async def test_get_by_id_found(test_session):
    """Тест: получение существующего резюме."""
    repo = PostgresResumeRepository(test_session)
    resume = ResumeFactory.create(profession="Python Developer")
    saved = await repo.save(resume)
    result = await repo.get_by_id(saved.id)
    
    assert result is not None
    assert result.id == saved.id
    assert result.profession == resume.profession
    assert result.full_text == resume.full_text


@pytest.mark.asyncio
async def test_get_by_id_not_found(test_session):
    """Тест: получение несуществующего резюме."""
    repo = PostgresResumeRepository(test_session)

    result = await repo.get_by_id(999)

    assert result is None


@pytest.mark.asyncio
async def test_get_by_hh_id_found(test_session):
    """Тест: получение резюме по HH ID."""
    repo = PostgresResumeRepository(test_session)
    resume = ResumeFactory.create(hh_resume_id="hh_12345")
    saved = await repo.save(resume)
    
    result = await repo.get_by_hh_id("hh_12345")
    
    assert result is not None
    assert result.id == saved.id
    assert result.hh_resume_id == "hh_12345"


@pytest.mark.asyncio
async def test_list_active(test_session):
    """Тест: получение всех активных резюме."""
    repo = PostgresResumeRepository(test_session)
    
    # Создаем активные и неактивные резюме
    active1 = ResumeFactory.create(profession="Dev1")
    active2 = ResumeFactory.create(profession="Dev2")
    inactive = ResumeFactory.create(profession="Dev3", is_active=False)
    
    await repo.save(active1)
    await repo.save(active2)
    await repo.save(inactive)
    
    results = await repo.list_active()
    
    assert len(results) == 2
    assert all(r.is_active for r in results)
    professions = {r.profession for r in results}
    assert "Dev1" in professions
    assert "Dev2" in professions


@pytest.mark.asyncio
async def test_get_by_profession(test_session):
    """Тест: получение резюме по профессии."""
    repo = PostgresResumeRepository(test_session)
    
    resume1 = ResumeFactory.create(profession="Python Developer")
    resume2 = ResumeFactory.create(profession="Python Developer")
    resume3 = ResumeFactory.create(profession="Java Developer")
    
    await repo.save(resume1)
    await repo.save(resume2)
    await repo.save(resume3)
    
    results = await repo.get_by_profession("Python Developer")
    
    assert len(results) == 2
    assert all(r.profession == "Python Developer" for r in results)


@pytest.mark.asyncio
async def test_delete_soft(test_session):
    """Тест: мягкое удаление резюме."""
    repo = PostgresResumeRepository(test_session)
    resume = ResumeFactory.create()
    saved = await repo.save(resume)
    
    result = await repo.delete(saved.id)
    
    assert result is True
    deleted = await repo.get_by_id(saved.id)
    assert deleted is not None
    assert deleted.is_active is False
