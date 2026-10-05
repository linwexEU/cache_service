import pytest

from src.exceptions.transform import DifferentLengthError, TransformedStringNotFoundError
from src.api.services.transform import TransformService


class TestTransform:
    async def test_repeated_creation(self) -> None:
        service = TransformService()

        created_id1 = await service.create_transform(
            ["first string", "second string", "third string"],
            ["other string", "another string", "last string"],
        )
        created_id2 = await service.create_transform(
            ["first string", "second string", "third string"],
            ["other string", "another string", "last string"],
        )

        assert created_id1 == created_id2

    async def test_different_length(self) -> None:
        service = TransformService()

        with pytest.raises(DifferentLengthError):
            await service.create_transform(
                ["first string", "second string"], ["other string", "another string", "last string"]
            )

    async def test_get_transformed_string(self) -> None:
        service = TransformService()

        created_id = await service.create_transform(
            ["first string", "second string"], ["other string", "another string"]
        )

        output = await service.get_transformed_string(created_id)

        assert output == "fir$t $tring, 0ther $tring, $ec0nd $tring, @n0ther $tring"

    async def test_transform_not_found(self) -> None:
        service = TransformService()

        with pytest.raises(TransformedStringNotFoundError):
            await service.get_transformed_string(999)
