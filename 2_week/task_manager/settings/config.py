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
    SYNC_MYSQL_DRIVER_NAME: str = "mysql+pymysql"
    ASYNC_MYSQL_DRIVER_NAME: str = "mysql+aiomysql"
    MYSQL_DB_READABLE_NAMES: list[str] = ["dbh", "dbl", "dbp_1", "dbp_2", "dbp_3", "dbp_4"]

    DB_MYSQL_HOST: str
    DB_MYSQL_PORT: str
    DB_MYSQL_USER: str = "user"
    DB_MYSQL_PASSWORD: str = "mysqlpwd"
    DB_MYSQL_DB: str = "auth-db"
    DB_MYSQL_POOL_SIZE: int = 5

    DBH_SQLALCHEMY_DATABASE_URI: Optional[AnyUrl] = None
    SYNC_DBH_SQLALCHEMY_DATABASE_URI: Optional[AnyUrl] = None

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
                database=values.get(f"{prefix}_DB"),
                username=values.get(f"{prefix}_USER"),
                password=values.get(f"{prefix}_PASSWORD"),
                host=values.get(f"{prefix}_HOST"),
                port=values.get(f"{prefix}_PORT"),
            ),
        )
        return url

    @validator("DBH_SQLALCHEMY_DATABASE_URI", pre=True)
    def dbh_mysql_dsn(cls, v: Optional[str], values: dict[str, Any]) -> Any:
        return cls._make_db_uri(
            prefix="DBH_MYSQL",
            driver=values["ASYNC_MYSQL_DRIVER_NAME"],
            value=v,
            values=values,
        )

    @validator("SYNC_DBH_SQLALCHEMY_DATABASE_URI", pre=True)
    def sync_dbh_mysql_dsn(cls, v: Optional[str], values: dict[str, Any]) -> Any:
        return cls._make_db_uri(
            prefix="DBH_MYSQL",
            driver=values["SYNC_MYSQL_DRIVER_NAME"],
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
