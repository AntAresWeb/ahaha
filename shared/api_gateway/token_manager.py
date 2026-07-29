import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import aiofiles
from pydantic import BaseModel

from shared.api_gateway.base import APIClient
from shared.api_gateway.exceptions import AuthenticationError
from shared.config.hh_api import HHAPISettings

logger = logging.getLogger(__name__)


class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: datetime  # UTC


class TokenManager:
    def __init__(
        self,
        client: APIClient,
        settings: HHAPISettings,
        refresh_threshold: int = 300,  # 5 минут
    ) -> None:
        self._client: APIClient = client
        self.client_id: str = settings.app_id
        self.client_secret: str = settings.app_secret
        self.token_url: str = settings.oauth_token_url
        self.refresh_threshold: int = refresh_threshold
        self.token_file: Path = Path(settings.token_file)
        self._token_data: TokenData | None = None

    async def get_access_token(self) -> str:
        if self._token_data is None:
            self._token_data = await self._load_token()
            if self._token_data is None:
                raise AuthenticationError(
                    "No token found. Please authenticate first.",
                )

        if self._token_data.expires_at - timedelta(seconds=self.refresh_threshold) < datetime.now(timezone.utc):
            logger.info("Token expired, refreshing...")
            await self._refresh_token()

        return self._token_data.access_token

    async def set_token(
        self,
        access_token: str,
        refresh_token: str,
        expires_in: int,
    ) -> None:
        self._token_data = TokenData(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=expires_in),
        )
        await self._save_token()
        logger.info("Token saved successfully to %s", self.token_file)

    async def _refresh_token(self) -> None:
        if self._token_data is None or not self._token_data.refresh_token:
            raise AuthenticationError("No refresh token available")

        logger.info("Refreshing token...")

        try:
            data = await self._client.post(
                url=self.token_url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self._token_data.refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )

            self._token_data = TokenData(
                access_token=data["access_token"],
                refresh_token=data.get("refresh_token", self._token_data.refresh_token),
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=data.get("expires_in", 3600)),
            )
            await self._save_token()
            logger.info("Token refreshed successfully")

        except Exception as e:
            logger.error("Failed to refresh token: %s", e)
            raise AuthenticationError(f"Token refresh failed: {e}") from e

    async def _load_token(self) -> TokenData | None:
        if not self.token_file.exists():
            return None

        try:
            async with aiofiles.open(self.token_file) as f:
                content = await f.read()
                data: dict[str, Any] = json.loads(content)

            return TokenData(
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                expires_at=datetime.fromisoformat(data["expires_at"]),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error("Failed to load token from %s: %s", self.token_file, e)
            return None

    async def _save_token(self) -> None:
        if self._token_data is None:
            return

        self.token_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "access_token": self._token_data.access_token,
            "refresh_token": self._token_data.refresh_token,
            "expires_at": self._token_data.expires_at.isoformat(),
        }

        content = json.dumps(data, indent=2)
        async with aiofiles.open(self.token_file, "w") as f:
            await f.write(content)
