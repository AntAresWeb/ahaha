from typing import Any, Self

import httpx

from shared.api_gateway.errors import handle_http_error


class APIClient:

    def __init__(self, timeout: int = 30) -> None:
        self.timeout: int = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> Self:
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
            )
        return self._client

    async def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        return await self.request("GET", url, headers=headers, params=params, timeout=timeout)

    async def post(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        return await self.request("POST", url, headers=headers, json=json, data=data, timeout=timeout)

    async def request(  # noqa: PLR0913
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        client = await self._get_client()
        request_timeout = timeout or self.timeout

        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
                data=data,
                timeout=request_timeout,
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise handle_http_error(e) from e

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
