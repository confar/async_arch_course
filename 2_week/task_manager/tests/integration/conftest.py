import asyncio
from os import environ
from typing import AsyncGenerator

import pytest
from dotenv import load_dotenv
from fastapi import FastAPI
from httpx import AsyncClient
from loguru import logger
from pydantic import AnyUrl
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import ConcreteBase
from sqlalchemy.orm import Session, scoped_session
from sqlalchemy_utils import create_database, database_exists, drop_database
from starlette.requests import Request

from app.api.base_deps import get_database_clients, get_dbh_client, get_dbl_client
from app.database import Database, DBLBase
from settings.config import Settings
from tests import factories


@pytest.fixture(autouse=True, scope="session")
def test_env() -> bool:
    test_environment_path = "settings/.env.local.test"
    load_dotenv(test_environment_path, override=is_local_test)
    return True


@pytest.fixture()
def app() -> FastAPI:
    from app.main import get_app

    return get_app()


@pytest.fixture(scope="session")
def event_loop(request):  # type: ignore
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def http_request() -> Request:
    return Request(scope={"type": "http"})


@pytest.fixture()
async def rest_client(
    async_dbl: AsyncSession,
    async_dbh: AsyncSession,
    app: FastAPI,
) -> AsyncGenerator[AsyncClient, None]:
    def _get_dbl_override() -> AsyncSession:
        return async_dbl

    def _get_db_clients_override() -> dict[str, AsyncSession]:
        return {"db": async_dbl}

    app.dependency_overrides[get_dbl_client] = _get_dbl_override
    app.dependency_overrides[get_dbh_client] = _get_dbh_override
    app.dependency_overrides[get_database_clients] = _get_db_clients_override
    async with AsyncClient(
        app=app,
        base_url="http://test",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client

    app.dependency_overrides = {}


@pytest.fixture(scope="session")
def test_settings(test_env: bool) -> Settings:
    from settings.config import get_settings

    return get_settings()


def _sync_session(
    db_sync_dsn: AnyUrl,
    db_schema_name: str,
    db_host: str,
    db_base: ConcreteBase,
    session_factory: scoped_session,
) -> Session:
    if not db_sync_dsn.endswith("test"):
        logger.error(
            "received dsn for database not ending on test - {db}, probably real db on host {host}, ",
            "terminate tests",
            db=db_schema_name,
            host=db_host,
        )
        return
    if database_exists(db_sync_dsn):
        logger.warning(
            "test database {db} already exists on host {host}, dropping it",
            db=db_schema_name,
            host=db_host,
        )
        drop_database(db_sync_dsn)
    create_database(db_sync_dsn)
    sync_engine = create_engine(db_sync_dsn, echo=True, isolation_level="READ COMMITTED")
    db_base.metadata.create_all(sync_engine)

    connection = sync_engine.connect()
    # http://factoryboy.readthedocs.io/en/latest/orms.html#managing-sessions
    session_factory.configure(bind=connection, autocommit=True)
    session = session_factory(autocommit=True)
    yield session

    # teardown
    session.close()
    session_factory.remove()
    connection.close()
    db_base.metadata.drop_all(sync_engine)
    logger.info(
        "dropping test database {db} host {host}",
        db=db_schema_name,
        host=db_host,
    )


@pytest.fixture(scope="session")
def sync_dbl_session(test_settings: Settings) -> Session:
    yield from _sync_session(
        db_sync_dsn=test_settings.SYNC_DBL_SQLALCHEMY_DATABASE_URI,
        db_schema_name=test_settings.DBL_MYSQL_DB,
        db_host=test_settings.DBL_MYSQL_HOST,
        db_base=DBLBase,
        session_factory=factories.DBLSession,
    )


def _sync_db(sync_session: Session, db_schema_name: str, db_host: str, db_base: ConcreteBase) -> Session:
    yield sync_session
    if not db_schema_name.endswith("test"):
        logger.error(
            "received dsn for database not ending on test - {db}, probably real db on host {host}, terminate tests",
            db=db_schema_name,
            host=db_host,
        )
        return
    for table in reversed(db_base.metadata.sorted_tables):
        sync_session.connection().engine.execute(table.delete())


@pytest.fixture()
def sync_dbl(sync_dbl_session: Session, test_settings: Settings) -> Session:
    yield from _sync_db(
        sync_session=sync_dbl_session,
        db_schema_name=test_settings.DBL_MYSQL_DB,
        db_host=test_settings.DBL_MYSQL_HOST,
        db_base=DBLBase,
    )


@pytest.fixture(scope="session")
async def async_dbl(test_settings: Settings) -> AsyncGenerator[AsyncSession, None]:
    db_async_dsn = test_settings.DBL_SQLALCHEMY_DATABASE_URI
    connect_kwargs = dict(**Database.CONNECT_KWARGS, pool_size=5)
    async_db = Database(db_connect_url=db_async_dsn, db_alias="dbl", connect_kwargs=connect_kwargs)
    yield async_db
    await async_db.disconnect()
