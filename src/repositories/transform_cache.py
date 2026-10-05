from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.models import TransformCache


class TransformCacheRepository:
    """String-level cache access; never commits — commit policy lives in UnitOfWork."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, input_str: str, transformed_str: str) -> TransformCache:
        """Stage a cache miss; flushed on UnitOfWork exit so concurrent readers stay consistent."""
        transform_cache = TransformCache(input_str=input_str, transformed_str=transformed_str)
        self.session.add(transform_cache)
        return transform_cache

    async def get_by_input_str(self, input_str: str) -> Optional[TransformCache]:
        """Lookup before transforming: a hit avoids the expensive transformer call."""
        return await self.session.scalar(
            select(TransformCache).where(TransformCache.input_str == input_str)
        )
