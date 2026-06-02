import asyncio
from dataclasses import dataclass, field

import httpx

from .config import HHAppSettings
from .interfaces import AuthManagerProtocol


@dataclass
class AuthApplicationManager(AuthManagerProtocol):
    """
    Реализация менеджера авторизации приложения.
    """
    settings: HHAppSettings

    _access_token: str | None = None
    _expires_in: int = 0
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def get_access_token(self) -> str:
        if self._access_token is None:
            async with self._lock:
                if self._access_token is None or self._is_token_expired():
                    await self._fetch_token()
        return self._access_token


    async def _fetch_token(self) -> None:
        """
        Выполняет запрос на получение нового access-токена.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.settings.oauth_token_url,
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.settings.client_id,
                    'client_secret': self.settings.client_secret,
                }
            )
            response.raise_for_status()
            token_data = response.json()
            self._access_token = token_data['access_token']
            self._expires_in = token_data.get('expires_in', 3600)
