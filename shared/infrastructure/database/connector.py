import logging
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import AsyncAdaptedQueuePool

from shared.config.postgres import (
    PostgresSettings,
    get_postgres_settings,
)

logger = logging.getLogger(__name__)


class PGConnector:
    """Управляет подключением к PostgreSQL."""

    def __init__(self, settings: PostgresSettings) -> None:
        self._settings = settings

        # Используем параметры из настроек
        self._database_url = settings.database_url
        self._pool_size = settings.db_pool_size
        self._max_overflow = settings.db_max_overflow
        self._pool_timeout = settings.db_pool_timeout
        self._echo = settings.db_echo
        self._pool_pre_ping = settings.db_pool_pre_ping
        self._pool_recycle = settings.db_pool_recycle

        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

        self._init_engine()
        self._init_session_factory()

        logger.info("PGConnector инициализирован для %s", settings.database_url_without_password)

    def _init_engine(self) -> None:
        """Создает асинхронный движок SQLAlchemy."""
        self._engine = create_async_engine(
            self._database_url,
            echo=self._echo,
            pool_size=self._pool_size,
            max_overflow=self._max_overflow,
            pool_timeout=self._pool_timeout,
            poolclass=AsyncAdaptedQueuePool,
            pool_pre_ping=self._pool_pre_ping,
            pool_recycle=self._pool_recycle,
        )
        logger.debug("Движок PostgreSQL создан")

    def _init_session_factory(self) -> None:
        """Создает фабрику асинхронных сессий."""
        if self._engine is None:
            raise RuntimeError("Движок не инициализирован")

        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        logger.debug("Фабрика сессий создана")

    @property
    def engine(self) -> AsyncEngine:
        """Возвращает движок SQLAlchemy."""
        if self._engine is None:
            raise RuntimeError("Движок не инициализирован")
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Возвращает фабрику сессий."""
        if self._session_factory is None:
            raise RuntimeError("Фабрика сессий не инициализирована")
        return self._session_factory

    async def dispose(self) -> None:
        """Закрывает все соединения."""
        if self._engine:
            await self._engine.dispose()
            logger.info("Движок PostgreSQL закрыт")


@lru_cache(maxsize=1)
def get_pg_connector() -> PGConnector:
    """
    Возвращает синглтон-экземпляр PGConnector.
    Создается один раз при первом вызове.
    """
    settings = get_postgres_settings()
    return PGConnector(settings)
