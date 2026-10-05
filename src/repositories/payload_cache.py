from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.models import PayloadCache


class PayloadCacheRepository:
    """Payload-level cache access; never commits — commit policy lives in UnitOfWork."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, interleaving: str, interleaving_hash: str) -> PayloadCache:
        """Stage a new payload; the unique hash is what enables id reuse across requests."""
        payload_cache = PayloadCache(
            interleaving=interleaving, interleaving_hash=interleaving_hash
        )
        self.session.add(payload_cache)
        return payload_cache

    async def get_by_hash(self, interleaving_hash: str) -> Optional[PayloadCache]:
        """Lookup by content hash: a hit means the payload id can be reused as-is."""
        return await self.session.scalar(
            select(PayloadCache).where(PayloadCache.interleaving_hash == interleaving_hash)
        )

    async def get_by_id(self, id: int) -> Optional[PayloadCache]:
        """Primary-key fetch for GET: reads never trigger the transformer."""
        return await self.session.get(PayloadCache, id)
