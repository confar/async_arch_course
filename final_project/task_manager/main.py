import asyncio
import json
import logging
import sys
from typing import Any

import aiokafka
import uvloop
from aiokafka import AIOKafkaConsumer
from fastapi import FastAPI, __version__
from loguru import logger

from app.api import api_router
from app.core.tasks.repositories import TaskRepository, TaskEventRepository
from app.core.tasks.services import TaskService
from app.database import Database
from app.log_handler import InterceptHandler
from settings.config import LogTypeEnum, Settings, get_settings

from app.core.tasks.models import DBBase

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

def serializer(value):
    return json.dumps(value).encode()

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
        loop = asyncio.get_event_loop()
        self.create_broker_pool(loop)
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
        self.app.add_event_handler("startup", self.create_tables)
        self.app.add_event_handler("shutdown", self.close_database_pool)


    def register_urls(self) -> None:
        self.app.include_router(api_router, prefix="/api")

    def create_database_pool(self, settings: Settings) -> None:
        databases = {}
        db_alias = 'db'
        uri = settings.DB_SQLALCHEMY_DATABASE_URI
        pool_size = settings.DB_POOL_SIZE
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
        await self.app.state.db.create_tables_by_base(DBBase)

    @staticmethod
    def serializer(value):
        return json.dumps(value).encode()

    def create_broker_pool(self, loop):
        producer = aiokafka.AIOKafkaProducer(bootstrap_servers='localhost:9092',
                                             value_serializer=self.serializer,
                                             compression_type="gzip", loop=loop)
        self.app.state.event_producer = producer


def get_app() -> FastAPI:
    return Application().setup()


if __name__ == "__main__":
    import uvicorn

    app = get_app()
    host = app.state.config.APP_HOST
    port = app.state.config.APP_PORT

    uvicorn.run(app, host=host, port=port)