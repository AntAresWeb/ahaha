# tests/test_client.py

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from src.hh_api_client.app.client import HHApiClient, create_api_client
from src.hh_api_client.app.interfaces import AuthManagerProtocol, HTTPClientProtocol


# Конфигурация для pytest
# Фикстура event_loop нужна для корректной работы с asyncio
@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# --- Фикстуры (Fixtures) ---

@pytest.fixture
def mock_settings():
    """Фикстура с настройками для тестов."""
    return HHApiSettings(
        client_id="test_client_id",
        client_secret="test_client_secret",
        base_api_url="https://api.test-hh.ru",
    )

@pytest.fixture
def mock_auth_manager():
    """Фикстура-заглушка для AuthManager."""
    # Создаем MagicMock, который реализует наш протокол
    # и имеет асинхронный метод get_access_token.
    manager = MagicMock(spec=AuthManagerProtocol)
    manager.get_access_token = AsyncMock(return_value="mocked_access_token_123")
    return manager

@pytest.fixture
def mock_http_client():
    """Фикстура-заглушка для HTTP-клиента."""
    client = MagicMock(spec=HTTPClientProtocol)
    
    # Настраиваем mock-ответ для метода .request()
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock() # Не будет вызывать ошибку
    mock_response.json = MagicMock(return_value={"items": [{"name": "Test Vacancy"}]})
    
    # Метод .request() должен быть асинхронным и возвращать наш mock-ответ
    client.request = AsyncMock(return_value=mock_response)
    
    return client

@pytest.fixture
def api_client(mock_settings, mock_auth_manager, mock_http_client):
    """Фикстура, которая создает экземпляр клиента с внедренными заглушками."""
    return HHApiClient(
        settings=mock_settings,
        auth_manager=mock_auth_manager,
        http_client=mock_http_client,
    )


# --- Сами тесты ---

@pytest.mark.asyncio
async def test_search_vacancies_success(api_client):
    """
    Тест проверяет, что метод search_vacancies:
    1.  Вызывает get_access_token у AuthManager.
    2.  Вызывает метод .request() у HTTP-клиента с правильными параметрами.
    3.  Возвращает распарсенный JSON-ответ.
    """
    params = {"text": "Python", "area": "1"}
    
    # Вызываем тестируемый метод
    result = await api_client.search_vacancies(params)
    
    # Проверки (Assertions)
    
    # 1. Проверяем, что метод получения токена был вызван ровно один раз.
    api_client.auth_manager.get_access_token.assert_awaited_once()
    
    # 2. Проверяем, что HTTP-запрос был вызван с правильными аргументами.
    api_client.http_client.request.assert_awaited_once()
    
    call_args = api_client.http_client.request.await_args_list[0]
    args, kwargs = call_args
    
    assert args == ("GET", "/vacancies")
    assert kwargs["params"] == params
    assert kwargs["headers"] == {"Authorization": "Bearer mocked_access_token_123"}
    
    # 3. Проверяем результат.
    assert result == {"items": [{"name": "Test Vacancy"}]}


@pytest.mark.asyncio
async def test_http_error_propagation(api_client):
    """
    Тест проверяет, что HTTP-ошибка (например, 404) корректно пробрасывается.
    """
    # Настраиваем mock, чтобы он вызывал ошибку при raise_for_status()
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 404
    mock_response.raise_for_status = MagicMock(
        side_effect=httpx.HTTPStatusError("404", request=MagicMock(), response=mock_response)
    )
    
    api_client.http_client.request = AsyncMock(return_value=mock_response)
    
    params = {"text": "NonExistent"}
    
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        await api_client.search_vacancies(params)
        
    assert exc_info.value.response.status_code == 404


@pytest.mark.asyncio
async def test_create_api_client_integration():
    """
    Интеграционный тест: проверяем, что фабрика create_api_client создает рабочие объекты.
    Здесь мы не мокаем ничего внутри, а проверяем создание и типы зависимостей.
    """
    # Используем кастомные настройки для теста
    settings = HHApiSettings(
        client_id="test_id",
        client_secret="test_secret",
        base_api_url="https://api.test-hh.ru",
        oauth_token_url="https://test.hh.ru/oauth/token",
        timeout=5.0,
    )
    
    client = create_api_client(settings)
    
    # Проверяем типы созданных объектов
    assert isinstance(client.settings, HHApiSettings)
    
    from hh_api_client.auth import AuthManager
    assert isinstance(client.auth_manager, AuthManager)
    
    from httpx import AsyncClient
    assert isinstance(client.http_client, AsyncClient)
    
    # Проверяем, что настройки передались в HTTP-клиент
    assert client.http_client.base_url == "https://api.test-hh.ru"
    assert client.http_client.timeout == 5.0
