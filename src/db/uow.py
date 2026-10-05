import types
from typing import Self

from src.repositories.payload_cache import PayloadCacheRepository
from src.repositories.transform_cache import TransformCacheRepository
from src.db.base import session_factory


class UnitOfWork:
    """Share one session across repos so each request commits atomically or not at all."""

    payload_cache_repo: PayloadCacheRepository
    transform_cache_repo: TransformCacheRepository

    async def __aenter__(self) -> Self:
        self.session = session_factory()
        self.payload_cache_repo = PayloadCacheRepository(self.session)
        self.transform_cache_repo = TransformCacheRepository(self.session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """Commit on clean exit, roll back on error — callers never manage transactions."""
        if exc_type is None:
            await self.session.commit()
        else:
            await self.session.rollback()
        await self.session.close()
