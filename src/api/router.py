from fastapi import APIRouter

from src.api.routers.transform import router as transform_router

router = APIRouter()

# Include routers
router.include_router(transform_router)
