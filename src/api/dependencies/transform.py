from typing import Annotated

from fastapi import Depends

from src.api.services.transform import TransformService


def get_transform_service() -> TransformService:
    """Indirection point so tests can swap the service via FastAPI dependency_overrides."""
    return TransformService()


TransformServiceDep = Annotated[TransformService, Depends(get_transform_service)]
