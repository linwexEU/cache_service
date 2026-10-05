from fastapi import FastAPI

from src.api.router import router as api_router
from src.utils.logger import config_logger

# Configure our logger
config_logger()


def create_app() -> FastAPI:
    """Factory (not just a global) so tests can build isolated app instances."""
    app = FastAPI()

    app.include_router(api_router)

    return app


app = create_app()
