# tests/conftest.py
import pytest

from src.vacancy_analizer.share.config import Settings


@pytest.fixture
def test_settings():
    """Фикстура с тестовыми настройками (без чтения реального .env)"""
    return Settings(
        hh_app_name="test_app/1.0 (test@example.com)",
        hh_app_id="test_app_id",
        hh_app_secret="test_app_secret",
        hh_redirect_uri="http://localhost:9999/auth/callback",
        token_file="test_tokens.json",
        log_level="DEBUG",
        http_timeout=30,
        max_retries=3,
    )
