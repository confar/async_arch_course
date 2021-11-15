import logging
from asyncio import current_task
from contextlib import AbstractContextManager, asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Callable

from sqlalchemy import inspect, literal, orm, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.ext.declarative import ConcreteBase, declarative_base
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class Base:
    @classmethod
    def get_real_column_name(cls, attr_name: str) -> str:
        return getattr(inspect(cls).c, attr_name).name


DBLBase: ConcreteBase = declarative_base(cls=Base)
DBHBase: ConcreteBase = declarative_base(cls=Base)


DBSessionFactory = Callable[..., AbstractContextManager[Session]]


@dataclass
class Database:
    CONNECT_KWARGS = {"max_overflow": 10, "pool_pre_ping": True, "pool_recycle": 3600, "echo_pool": True}

    def __init__(self, db_connect_url: str, db_alias: str, connect_kwargs: dict[str, Any], debug: bool = True) -> None:
        self._engine = create_async_engine(url=db_connect_url, **connect_kwargs, echo=debug)
        self._db_alias = db_alias
        self._async_session = async_scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                class_=AsyncSession,
                expire_on_commit=False,
                bind=self._engine,
            ),
            scopefunc=current_task,
        )

    async def create_tables_by_base(self, sqlalchemy_base: declarative_base) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(sqlalchemy_base.metadata.create_all)

    async def get_status(self) -> dict[str, str]:
        async with self.session() as session:
            db_status = await session.execute(
                select(
                    [
                        literal("ready").label("status"),
                        literal(self._db_alias).label("name"),
                    ],
                ),
            )
            return db_status.first()._asdict()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[Session, None]:
        session: Session = self._async_session()
        try:
            yield session
        except Exception:
            logger.exception("Session rollback because of exception")
            await session.rollback()
            raise
        finally:
            await session.close()
            await self._async_session.remove()

    async def disconnect(self) -> None:
        await self._engine.dispose()
