# auth.py
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import httpx
from config import get_settings
from fastapi import HTTPException
from models import TokenResponse, TokenSet

settings = get_settings()


class TokenStorage:
    """Управление хранением токенов с использованием pathlib"""

    def __init__(self) -> None:
        # Определяем путь к файлу токенов через pathlib
        self.token_path = Path(settings.token_file)

    def _ensure_directory_exists(self) -> None:
        """Создает директорию для файла токенов, если она не существует"""
        parent_dir = self.token_path.parent
        if parent_dir and not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> TokenSet | None:
        """Загружает токены из файла"""
        if not self.token_path.exists():
            return None

        try:
            with self.token_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                print(f">>> token {data}")
                data["expires_at"] = datetime.fromisoformat(data["expires_at"])
                return TokenSet(**data)
        except (json.JSONDecodeError, KeyError, ValueError, OSError) as e:
            print(f"Ошибка загрузки токенов из {self.token_path}: {e}")
            return None

    def save(self, tokens: TokenSet) -> None:
        """Сохраняет токены в файл"""
        # Убеждаемся, что директория существует
        self._ensure_directory_exists()

        with self.token_path.open("w", encoding="utf-8") as f:
            data = {
                "access_token": tokens.access_token,
                "refresh_token": tokens.refresh_token,
                "expires_at": tokens.expires_at.isoformat(),
            }
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Устанавливаем безопасные права доступа (только для владельца)
        if hasattr(self.token_path, "chmod"):
            # 0o600 = read-write only for owner
            self.token_path.chmod(0o600)

    def clear(self) -> None:
        """Удаляет файл с токенами"""
        if self.token_path.exists():
            self.token_path.unlink()

    def get_token_info(self) -> dict:
        """Возвращает информацию о файле токенов (размер, время создания и т.д.)"""
        if not self.token_path.exists():
            return {"exists": False}

        stat = self.token_path.stat()
        return {
            "exists": True,
            "size_bytes": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "path": str(self.token_path.absolute()),
        }


class HHAuthClient:
    """Клиент для работы с OAuth HH.ru (асинхронный)"""

    def __init__(self) -> None:
        self.token_storage = TokenStorage()
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Получает или создает HTTP клиент"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=settings.http_timeout, limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        return self._client

    async def close(self) -> None:
        """Закрывает HTTP клиент"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def get_authorization_url(self) -> str:
        """Генерирует URL для авторизации"""
        return (
            f"{settings.oauth_authorize_url}"
            f"?response_type=code"
            f"&client_id={settings.hh_client_id}"
            f"&redirect_uri={settings.hh_redirect_uri}"
        )

    async def exchange_code_for_tokens(self, code: str) -> TokenSet:
        """Обменивает authorization_code на токены"""
        client = await self._get_client()

        data = {
            "grant_type": "authorization_code",
            "client_id": settings.hh_client_id,
            "client_secret": settings.hh_client_secret,
            "code": code,
            "redirect_uri": settings.hh_redirect_uri,
        }

        response = await client.post(settings.oauth_token_url, data=data)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail=f"Ошибка обмена кода на токены: {response.text}",
            )

        token_response = TokenResponse(**response.json())

        token_set = TokenSet(
            access_token=token_response.access_token,
            refresh_token=token_response.refresh_token,
            expires_at=datetime.now() + timedelta(seconds=token_response.expires_in),
        )

        self.token_storage.save(token_set)
        return token_set

    async def refresh_access_token(self, refresh_token: str) -> TokenSet | None:
        """Обновляет access_token с помощью refresh_token"""
        client = await self._get_client()

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": settings.hh_client_id,
            "client_secret": settings.hh_client_secret,
        }

        response = await client.post(settings.oauth_token_url, data=data)

        if response.status_code == 200:
            token_response = TokenResponse(**response.json())
            token_set = TokenSet(
                access_token=token_response.access_token,
                refresh_token=token_response.refresh_token,
                expires_at=datetime.now() + timedelta(seconds=token_response.expires_in),
            )
            self.token_storage.save(token_set)
            print(f"[{datetime.now()}] Токены успешно обновлены в {self.token_storage.token_path}")
            return token_set
        else:
            print(f"[{datetime.now()}] Ошибка обновления токенов: {response.status_code} - {response.text}")
            return None

    async def get_valid_access_token(self) -> str:
        """
        Возвращает валидный access_token.
        Если токен истек или скоро истечет, автоматически обновляет.
        """
        tokens = self.token_storage.load()

        if not tokens:
            raise HTTPException(status_code=401, detail="Нет сохраненных токенов. Выполните GET /auth/login")

        # Проверяем, нужно ли обновить токен
        if tokens.needs_refresh:
            print(f"[{datetime.now()}] Токен истекает через {tokens.expires_in_seconds}с, обновляем...")
            new_tokens = await self.refresh_access_token(tokens.refresh_token)
            if new_tokens:
                return new_tokens.access_token
            else:
                raise HTTPException(
                    status_code=401,
                    detail="Не удалось обновить токен. Требуется повторная авторизация через GET /auth/login",
                )

        if not tokens.is_valid:
            # Токен истек, пробуем обновить
            print(f"[{datetime.now()}] Токен истек, пробуем обновить...")
            new_tokens = await self.refresh_access_token(tokens.refresh_token)
            if new_tokens:
                return new_tokens.access_token
            else:
                raise HTTPException(
                    status_code=401,
                    detail="Токен истек и не может быть обновлен. Требуется повторная авторизация через GET /auth/login",
                )

        return tokens.access_token

    def get_status(self) -> dict:
        """Возвращает статус текущих токенов"""
        tokens = self.token_storage.load()
        token_info = self.token_storage.get_token_info()

        if not tokens:
            return {
                "status": "no_tokens",
                "message": "Токены не найдены. Выполните GET /auth/login",
                "token_file": token_info,
            }

        time_left = tokens.expires_in_seconds

        return {
            "status": "valid" if tokens.is_valid else "expired",
            "expires_at": tokens.expires_at.isoformat(),
            "time_left_seconds": time_left,
            "time_left_human": str(timedelta(seconds=time_left)),
            "needs_refresh": tokens.needs_refresh(settings.auto_refresh_threshold_seconds),
            "token_file": token_info,
        }

    def logout(self) -> None:
        """Удаляет сохраненные токены"""
        self.token_storage.clear()
        print(f"[{datetime.now()}] Токены удалены из {self.token_storage.token_path}")


# Глобальный экземпляр клиента
auth_client = HHAuthClient()
