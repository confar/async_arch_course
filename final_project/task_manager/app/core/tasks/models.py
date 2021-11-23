import enum
import uuid
from typing import Any

from sqlalchemy import Column, INTEGER, VARCHAR, func, ForeignKey, TEXT
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, ENUM
from sqlalchemy.ext.declarative import ConcreteBase, declarative_base

DBBase: ConcreteBase = declarative_base()


class DisplayValuesMixin:
    __members__: dict[Any, Any]

    @classmethod
    def display_values(cls) -> tuple[str, ...]:
        return tuple(str(item.value) for name, item in cls.__members__.items())


class RoleEnum(str, DisplayValuesMixin, enum.Enum):
    admin = "admin"
    analytics = "analytics"
    worker = "worker"
    manager = "manager"
    accounting = "accounting"


class StatusEnum(str, DisplayValuesMixin, enum.Enum):
    open = "open"
    done = "done"

ADMIN_ROLES = {RoleEnum.admin.value, RoleEnum.manager.value}
ASSIGNABLE_ROLES = {RoleEnum.analytics.value, RoleEnum.worker.value, RoleEnum.accounting.value}


class TaskORM(DBBase):

    __tablename__ = "tasks"

    id = Column(INTEGER(), autoincrement=True, primary_key=True)
    status = Column(ENUM(*StatusEnum.display_values(), name='Status'), doc="Статус задачи")
    public_id = Column(UUID(as_uuid=True), default=uuid.uuid4)

    assignee_id = Column(INTEGER(), ForeignKey("workers.id"))
    creator_id = Column(INTEGER(), ForeignKey("workers.id"))

    description = Column(VARCHAR(length=100), nullable=True)

    created_at = Column(TIMESTAMP, nullable=True, server_default=func.now())


class WorkerORM(DBBase):
    __tablename__ = "workers"

    id = Column(INTEGER(), autoincrement=True, primary_key=True)
    public_id = Column(TEXT())
    role = Column(ENUM(*RoleEnum.display_values(), name='Role'), doc="Тип роли")


