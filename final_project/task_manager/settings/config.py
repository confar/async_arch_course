from enum import Enum
from typing import Any, Optional

from dotenv import load_dotenv
from pydantic import AnyUrl, BaseSettings, HttpUrl, validator
from sqlalchemy.engine import URL

load_dotenv("settings/.env")


class LogTypeEnum(str, Enum):
    JSON = "json"
    PLAIN = "plain"


class LogLevelEnum(str, Enum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"
    NOTSET = ""


class SentrySettings(BaseSettings):
    SENTRY_DSN: Optional[HttpUrl]
    SENTRY_ENVIRONMENT: Optional[str]


class DBSettings(BaseSettings):
    SYNC_DRIVER_NAME: str = "postgresql"
    ASYNC_DRIVER_NAME: str = "postgresql+asyncpg"
    MYSQL_DB_READABLE_NAMES: list[str] = ["db"]

    DB_HOST: str
    DB_PORT: str
    DB_USER: str = "user"
    DB_PASSWORD: str = "mysqlpwd"
    DB_NAME: str = "task-manager-db"
    DB_POOL_SIZE: int = 5

    DB_SQLALCHEMY_DATABASE_URI: Optional[AnyUrl] = None
    SYNC_DB_SQLALCHEMY_DATABASE_URI: Optional[AnyUrl] = None

    @staticmethod
    def _make_db_uri(
            prefix: str,
            driver: str,
            value: Optional[str],
            values: dict[str, Any],
    ) -> str:
        """
        Возвращает uri для заданной базы
        Args:
            prefix: str - префикс в названии заданной базы
            driver: str - драйвер, используемый для коннекта к базе
            value: Optional[str] - значение, переданное в валидируемое поле
            values: Dict[str, Any] - словарь значений переданных в модель

        Returns:
            str - uri для заданного шарда dbp
        """
        if isinstance(value, str):
            return value
        url = str(
            URL.create(
                drivername=driver,
                database=values.get(f"{prefix}_NAME"),
                username=values.get(f"{prefix}_USER"),
                password=values.get(f"{prefix}_PASSWORD"),
                host=values.get(f"{prefix}_HOST"),
                port=values.get(f"{prefix}_PORT"),
            ),
        )
        return url

    @validator("DB_SQLALCHEMY_DATABASE_URI", pre=True, check_fields=False )
    def db_dsn(cls, v: Optional[str], values: dict[str, Any]) -> Any:
        return cls._make_db_uri(
            prefix="DB",
            driver=values["ASYNC_DRIVER_NAME"],
            value=v,
            values=values,
        )

    @validator("SYNC_DB_SQLALCHEMY_DATABASE_URI", pre=True, check_fields=False )
    def sync_db_dsn(cls, v: Optional[str], values: dict[str, Any]) -> Any:
        return cls._make_db_uri(
            prefix="DB",
            driver=values["SYNC_DRIVER_NAME"],
            value=v,
            values=values,
        )


class OpenAPISettings(BaseSettings):
    OPENAPI_URL: str = "/openapi.json"
    OPENAPI_FETCHING_SERVER: str = "/"


class Settings(SentrySettings, DBSettings, OpenAPISettings, BaseSettings):
    PROJECT_NAME: str = "auth"
    APP_HOST: str
    APP_PORT: int
    STAGE: str = "dev"
    TESTING: bool = STAGE in {"runtests"}
    DEBUG: bool = STAGE in {"dev", "test"}
    SECRET_KEY: str = "secret"

    LOG_LEVEL: LogLevelEnum
    LOG_TYPE: LogTypeEnum

    class Config:
        case_sensitive = True


def get_settings() -> Settings:
    return Settings()
