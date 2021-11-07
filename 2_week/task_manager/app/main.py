import asyncio
import logging
import sys

import uvloop
from fastapi import FastAPI, __version__
from fastapi.exceptions import RequestValidationError
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import api_router
from app.api.exceptions import (
    BaseAPIException,
    generic_http_exception_handler,
    on_api_exception,
    validation_exception_handler,
)
from app.database import Database, DBHBase, DBLBase
from app.log_handler import InterceptHandler
from settings.config import LogTypeEnum, Settings, get_settings

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class Application:
    def setup(self) -> FastAPI:
        settings = get_settings()
        self.app = FastAPI(
            version=__version__,
            title="Auth API",
            description="Python API for popug auth service",
            debug=settings.DEBUG,
            openapi_url=settings.OPENAPI_URL,
            servers=[
                {"url": settings.OPENAPI_FETCHING_SERVER},
            ],
        )
        self.app.state.config = settings
        self.create_database_pool(settings)
        self.configure_logging(settings)

        self.register_urls()
        self.configure_hooks()

        return self.app

    @staticmethod
    def configure_logging(settings: Settings) -> None:
        logging_level = settings.LOG_LEVEL.name
        log_type = settings.LOG_TYPE

        logging.root.handlers = [InterceptHandler()]
        logging.root.setLevel(logging_level)

        _loggers = logging.root.manager.loggerDict.keys()

        # In case of `--no-access-log` uvicorn flag, we shouldn't reconfigure its logger
        # See: https://github.com/encode/uvicorn/blob/master/uvicorn/config.py#L402
        loggers = list(_loggers)
        if "uvicorn.access" in loggers:
            loggers.remove("uvicorn.access")

        for name in loggers:
            logging.getLogger(name).handlers = []
            logging.getLogger(name).propagate = True

        logger.configure(
            handlers=[
                {
                    "sink": sys.stdout,
                    "level": logging_level,
                    "serialize": log_type == LogTypeEnum.JSON,
                },
            ],
        )

    def configure_hooks(self) -> None:
        self.setup_exception_handlers()
        self.app.add_event_handler("startup", self.create_tables)
        self.app.add_event_handler("shutdown", self.close_database_pool)

    def register_urls(self) -> None:
        self.app.include_router(api_router, prefix="/api")

    def setup_exception_handlers(self) -> None:
        self.app.add_exception_handler(RequestValidationError, validation_exception_handler)
        self.app.add_exception_handler(BaseAPIException, on_api_exception)
        self.app.add_exception_handler(StarletteHTTPException, generic_http_exception_handler)

    def create_database_pool(self, settings: Settings) -> None:
        databases = {}
        for db_alias in settings.MYSQL_DB_READABLE_NAMES:
            uri = getattr(settings, f"{db_alias.upper()}_SQLALCHEMY_DATABASE_URI")
            pool_size = getattr(settings, f"{db_alias.upper()}_MYSQL_POOL_SIZE")
            db = Database(
                db_connect_url=uri,
                db_alias=db_alias,
                connect_kwargs=dict(**Database.CONNECT_KWARGS, pool_size=pool_size),
                debug=settings.DEBUG,
            )
            logger.info("creating database connection for {}", db_alias)
            setattr(self.app.state, db_alias, db)
            databases[db_alias] = db
        self.app.state.databases = databases

    async def close_database_pool(self) -> None:
        for db_alias, db in self.app.state.databases.items():
            logger.info("closing database pool for db {}", db_alias)
            try:
                await db.disconnect()
            except Exception as exc:
                logger.warning("failed to close database pool {} due to {}", db_alias, exc)
                continue

    async def create_tables(self) -> None:
        await self.app.state.dbl.create_tables_by_base(DBLBase)
        await self.app.state.dbh.create_tables_by_base(DBHBase)


def get_app() -> FastAPI:
    return Application().setup()


if __name__ == "__main__":
    import uvicorn

    app = get_app()
    host = app.state.config.APP_HOST
    port = app.state.config.APP_PORT

    uvicorn.run(app, host=host, port=port)
