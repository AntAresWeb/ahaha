import os
import pytest
from src.vacancy_analizer.share.config import get_settings


@pytest.fixture
def clean_env():
    """Очищает переменные окружения перед тестом"""
    env_backup = dict(os.environ)
    # Удаляем все переменные HH_*
    for key in list(os.environ.keys()):
        if key.startswith("HH_") or key in ["TOKEN_FILE", "LOG_LEVEL", "HTTP_TIMEOUT", "MAX_RETRIES"]:
            del os.environ[key]
    yield
    os.environ.clear()
    os.environ.update(env_backup)


def test_load_settings_from_env(clean_env, tmp_path):
    """Проверяет загрузку настроек из переменных окружения"""
    # Устанавливаем тестовые переменные
    os.environ["HH_APP_NAME"] = "test_app/1.0 (test@example.com)"
    os.environ["HH_APP_ID"] = "test_client_id"
    os.environ["HH_APP_SECRET"] = "test_client_secret"
    os.environ["HH_REDIRECT_URI"] = "http://localhost:8080/auth/callback"
    os.environ["TOKEN_FILE"] = str(tmp_path / "test_tokens.json")
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["HTTP_TIMEOUT"] = "60"
    os.environ["MAX_RETRIES"] = "5"
    
    settings = get_settings()
    
    assert settings.hh_app_name == "test_app/1.0 (test@example.com)"
    assert settings.hh_app_id == "test_client_id"
    assert settings.hh_app_secret == "test_client_secret"
    assert settings.hh_redirect_uri == "http://localhost:8080/auth/callback"
    assert settings.token_file == str(tmp_path / "test_tokens.json")
    assert settings.log_level == "DEBUG"
    assert settings.http_timeout == 60
    assert settings.max_retries == 5


def test_default_values(clean_env):
    """Проверяет значения по умолчанию, когда переменные окружения не заданы"""

    settings = get_settings()
    
    assert settings.hh_redirect_uri == "http://localhost:8080/auth/callback"
    assert settings.log_level == "INFO"
    assert settings.http_timeout == 30
    assert settings.max_retries == 3
    assert settings.auto_refresh_threshold_seconds == 300
