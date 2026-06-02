from typing import Protocol, runtime_checkable

import httpx


@runtime_checkable
class AuthManagerProtocol(Protocol):
    """
    Абстрактный протокол для менеджера авторизации.
    Любая реализация этого протокола должна иметь метод get_access_token.
    """
    async def get_access_token(self) -> str:
        ...

@runtime_checkable
class HTTPClientProtocol(Protocol):
    """
    Абстрактный протокол для HTTP-клиента.
    Мы будем использовать его, чтобы отвязаться от конкретной библиотеки (httpx).
    """
    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        ...
