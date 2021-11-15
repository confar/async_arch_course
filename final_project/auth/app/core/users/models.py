import enum
import uuid
from typing import Dict, Any
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy import Column, INTEGER, VARCHAR, func, TEXT
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.declarative import ConcreteBase, declarative_base

DBBase: ConcreteBase = declarative_base()


class DisplayValuesMixin:
    __members__: Dict[Any, Any]

    @classmethod
    def display_values(cls) -> tuple[str, ...]:
        return tuple(str(item.value) for name, item in cls.__members__.items())


class RoleEnum(str, DisplayValuesMixin, enum.Enum):
    admin = "admin"
    analytics = "analytics"
    worker = "worker"
    accounting = "accounting"


class UserORM(DBBase):

    __tablename__ = "users"

    id = Column(INTEGER(), autoincrement=True, primary_key=True)
    email = Column(VARCHAR(length=50))
    public_id = Column(UUID(as_uuid=True), default=uuid.uuid4)
    password_hash = Column(TEXT())

    first_name = Column(VARCHAR(length=100), nullable=True)
    last_name = Column(VARCHAR(length=100), nullable=True)

    created_at = Column(TIMESTAMP, nullable=True, server_default=func.now())
    role = Column(ENUM(*RoleEnum.display_values(), name='Role'), doc="Тип роли")

