from typing import Literal

from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

env_file = find_dotenv("src/.env")
load_dotenv(env_file)


class Settings(BaseSettings):
    """Runtime configuration from environment/.env, so containers need no code changes."""
    model_config = SettingsConfigDict(env_file=env_file)

    MODE: Literal["DEV", "TEST"]

    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    TEST_DB_USER: str
    TEST_DB_PASS: str
    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_NAME: str

    @property
    def DATABASE_URL(self) -> str:
        """Assembled here so only one place knows the async URL shape (asyncpg)."""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def TEST_DATABASE_URL(self) -> str:
        """Separate test database so integration tests can drop/create without touching dev data."""
        return f"postgresql+asyncpg://{self.TEST_DB_USER}:{self.TEST_DB_PASS}@{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"


settings = Settings()  # type: ignore
