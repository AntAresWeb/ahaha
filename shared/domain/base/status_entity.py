"""Базовый класс для сущностей со статусом."""
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Generic, TypeVar

StatusT = TypeVar("StatusT", bound=Enum)


@dataclass
class StatusEntity(ABC, Generic[StatusT]):
    """
    Базовый класс для сущностей, имеющих статус.

    Предоставляет общую логику работы со статусами:
    - Хранение статуса
    - Подсчет попыток
    - Отслеживание времени создания и обновления
    """

    id: int | None = None
    status: StatusT
    retry_count: int = 0
    error_message: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = None

    def _update_timestamp(self) -> None:
        """Обновить временную метку изменения."""
        self.updated_at = datetime.now(timezone.utc)

    def mark_status(self, new_status: StatusT) -> None:
        """Установить новый статус с обновлением времени."""
        self.status = new_status
        self._update_timestamp()

    def mark_error(self, error: str, status: StatusT | None = None) -> None:
        """Зафиксировать ошибку с возможностью смены статуса."""
        self.error_message = error
        self.retry_count += 1
        if status is not None:
            self.status = status
        self._update_timestamp()
