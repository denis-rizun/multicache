import logging
from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.utils import BASE_MODEL_CONFIG


class APISettings(BaseSettings):
    model_config = SettingsConfigDict(**BASE_MODEL_CONFIG, env_prefix="API_")

    NAME: str = "Cache API"
    VERSION: str = "1.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    ALLOWED_HOSTS: list[str] = ["http://localhost:3000"]
    ALLOW_CREDENTIALS: bool = True
    ALLOWED_METHODS: list[str] = ["*"]
    ALLOWED_HEADERS: list[str] = ["*"]


class LoggerSettings(BaseSettings):
    model_config = SettingsConfigDict(**BASE_MODEL_CONFIG, env_prefix="LOGGING_")

    LEVEL: int = 0
    LEVEL_NAME: str = "INFO"

    @model_validator(mode="after")
    def set_level(self) -> Self:
        self.LEVEL = logging.getLevelNamesMapping().get(self.LEVEL_NAME.upper(), logging.INFO)
        return self


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(**BASE_MODEL_CONFIG, env_prefix="POSTGRES_")

    DATABASE: str = ""
    USER: str = ""
    PASSWORD: SecretStr = SecretStr("")
    HOST: str = ""
    PORT: int = 0
    POOL_SIZE: int = 5
    POOL_TIMEOUT_S: float = 10.0

    TEST_DATABASE: str = ""

    def get_url(self, driver: str | None = "asyncpg") -> str:
        return self._build_url(self.DATABASE, driver)

    def get_test_url(self, driver: str | None = "asyncpg") -> str:
        return self._build_url(self.TEST_DATABASE, driver)

    def _build_url(self, database: str, driver: str | None) -> str:
        driver = f"+{driver}" if driver else ""
        return f"postgresql{driver}://{self.USER}:{self.PASSWORD.get_secret_value()}@{self.HOST}:{self.PORT}/{database}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(**BASE_MODEL_CONFIG)

    ENV: Literal["DEV", "PROD"] = "PROD"
    api: APISettings = Field(default_factory=APISettings)
    logging: LoggerSettings = Field(default_factory=LoggerSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    @classmethod
    @lru_cache
    def get_instance(cls) -> Self:
        return cls()


config = Settings.get_instance()
