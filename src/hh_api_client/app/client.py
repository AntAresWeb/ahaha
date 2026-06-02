import logging
from typing import Any

from http import HTTPStatus

import httpx
from httpx import HTTPError, HTTPStatusError

from .config import HHAppSettings
from .interfaces import AuthManagerProtocol, HTTPClientProtocol

logger = logging.getLogger(__name__)


class HHApiClient:
    """Асинхронный клиент для HeadHunter API."""

    def __init__(
        self,
        settings: HHAppSettings,
        auth_manager: AuthManagerProtocol,
        http_client: HTTPClientProtocol,
    ) -> None:
        self.settings = settings
        self.auth_manager = auth_manager # Зависимость внедряется извне
        self.http_client = http_client   # Зависимость внедряется извне


    async def close(self) -> None:
        """Пытаемся закрыть клиента, если у него есть такой метод."""
        if hasattr(self.http_client, "aclose") and callable(self.http_client.aclose):
            await self.http_client.aclose()


    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        try:
            token = await self.auth_manager.get_access_token()
            headers = {"Authorization": f"Bearer {token}"}
            response = await self.http_client.request(
                method, url, params=params, headers=headers, timeout=self.settings.timeout
            )
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as exc:
            if exc.response.status_code == HTTPStatus.UNAUTHORIZED:
                logger.warning("Получен 401 Unauthorized. Пробуем обновить токен.")
                await self.auth_manager._fetch_token() 
                new_token = await self.auth_manager.get_access_token()
                headers = {"Authorization": f"Bearer {new_token}"}
                retry_response = await self.http_client.request(
                    method, url, params=params, headers=headers
                )
                retry_response.raise_for_status()
                return retry_response.json()
            else:
                logger.error(f"HTTP Error {exc.response.status_code} при запросе к {url}")
                raise
        except HTTPError as exc:
            logger.error(f"Ошибка сети при запросе к {url}: {exc}")
            raise


    async def search_vacancies(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Поиск вакансий.
        Args:
            params: Словарь параметров для поиска (text, area, experience и т.д.)
        Returns:
            Словарь с результатами поиска в формате API HH.
        """
        return await self._make_request("GET", "/vacancies", params=params)


def create_api_client(settings: HHAppSettings | None = None) -> HHApiClient:
    """
    Фабричная функция для создания полностью сконфигурированного клиента.
    Args:
        settings: Опционально. Если None, настройки будут загружены из .env.
    Returns:
        Экземпляр HHApiClient, готовый к использованию.
    """
    if settings is None:
        settings = HHAppSettings() # Загрузка из .env по умолчанию

    # Создаем конкретные реализации зависимостей
    auth_manager = AuthManager(settings=settings)
    
    # Создаем и настраиваем HTTP-клиент
    http_client = httpx.AsyncClient(
        base_url=settings.base_api_url,
        timeout=settings.timeout,
        follow_redirects=True,
    )
    
    # Собираем и возвращаем итоговый клиент
    return HHApiClient(
        settings=settings,
        auth_manager=auth_manager,
        http_client=http_client,
    )
