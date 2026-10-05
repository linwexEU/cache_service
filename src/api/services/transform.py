import asyncio

from src.exceptions.transform import DifferentLengthError, TransformedStringNotFoundError
from src.db.uow import UnitOfWork
from src.utils.security import security


class TransformService:
    """Builds payloads while minimizing transformer calls and reusing payload ids."""

    async def create_transform(self, input_lst1: list[str], input_lst2: list[str]) -> int:
        """Return the existing payload id for repeated inputs; transform only cache misses."""
        if len(input_lst1) != len(input_lst2):
            raise DifferentLengthError()

        transformed_lst1, transformed_lst2 = await asyncio.gather(
            self._get_transformed_strings(input_lst1), self._get_transformed_strings(input_lst2)
        )

        interleaving = self._interleaving(transformed_lst1, transformed_lst2)
        hash_interleaving = security.hash(interleaving)

        async with UnitOfWork() as uow:
            cached = await uow.payload_cache_repo.get_by_hash(hash_interleaving)
            if cached is None:
                cached = await uow.payload_cache_repo.create(interleaving, hash_interleaving)

        return cached.id

    async def get_transformed_string(self, id: int) -> str:
        """Serve reads from the payload cache; the transformer never runs on GET."""
        async with UnitOfWork() as uow:
            payload_cache = await uow.payload_cache_repo.get_by_id(id)
            if payload_cache is None:
                raise TransformedStringNotFoundError()
        return payload_cache.interleaving

    async def _get_transformed_strings(self, input_lst: list[str]) -> list[str]:
        """Cache-aside per string: the transformer simulates an expensive external call."""
        transformed_strings = []
        async with UnitOfWork() as uow:
            for input_str in input_lst:
                result = await uow.transform_cache_repo.get_by_input_str(input_str)

                if result is None:
                    transformed_str = self._transform(input_str)
                    await uow.transform_cache_repo.create(input_str, transformed_str)
                    transformed_strings.append(transformed_str)
                else:
                    transformed_strings.append(result.transformed_str)
        return transformed_strings

    def _transform(self, input_str: str) -> str:
        """Stand-in for the external service; deterministic so outputs stay reproducible."""
        symbols = {"s": "$", "l": "1", "ch": "4", "o": "0", "a": "@"}
        for i in input_str:
            if i not in symbols:
                continue
            input_str = input_str.replace(i, symbols[i])
        return input_str

    def _interleaving(self, input_lst1: list[str], input_lst2: list[str]) -> str:
        """Interleave both transformed lists positionally, per the task contract."""
        result = []
        for item in zip(input_lst1, input_lst2):
            result.extend(item)
        return ", ".join(result)
