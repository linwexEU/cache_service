import logging

from fastapi import APIRouter, HTTPException, status

from src.exceptions.transform import DifferentLengthError, TransformedStringNotFoundError
from src.api.dependencies.transform import TransformServiceDep
from src.schemas.transform import (
    CreateTransformRequest,
    CreateTransformResponse,
    GetTransformResponse,
)
from src.exceptions.base import AppError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/payload")
async def create_transform(
    payload: CreateTransformRequest, service: TransformServiceDep
) -> CreateTransformResponse:
    """Create (or reuse) a payload; domain errors become HTTP codes, never tracebacks."""
    try:
        created_id = await service.create_transform(payload.input_lst1, payload.input_lst2)
    except DifferentLengthError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Different length of the input lists"
        )
    except AppError as err:
        logger.error("Internal server error: %s", err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return CreateTransformResponse(created_id=created_id)


@router.get("/payload/{id}")
async def get_transform(id: int, service: TransformServiceDep) -> GetTransformResponse:
    """Fetch a generated payload by id; unknown ids are 404, not 500."""
    try:
        output = await service.get_transformed_string(id)
    except TransformedStringNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transformed string not found"
        )
    except AppError as err:
        logger.error("Internal server error: %s", err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return GetTransformResponse(output=output)
