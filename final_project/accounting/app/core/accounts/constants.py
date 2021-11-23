# to get a string like this run:
# openssl rand -hex 32
import enum
from typing import Any

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class DisplayValuesMixin:
    __members__: dict[Any, Any]

    @classmethod
    def display_values(cls) -> tuple[str, ...]:
        return tuple(str(item.value) for name, item in cls.__members__.items())


class Role(str, DisplayValuesMixin, enum.Enum):
    admin = "admin"
    analytics = "analytics"
    worker = "worker"
    manager = "manager"
    accounting = "accounting"


class Status(str, DisplayValuesMixin, enum.Enum):
    open = "open"
    closed = "closed"


class PaymentStatus(str, DisplayValuesMixin, enum.Enum):
    initiated = "initiated"
    payed = "payed"


class CreditDebit(str, DisplayValuesMixin, enum.Enum):
    credit = "credit"
    debit = "debit"


class TransactionType(str, DisplayValuesMixin, enum.Enum):
    deposit = "deposit"
    withdraw = "withdraw"
    payment = "payment"


class Period(str, DisplayValuesMixin, enum.Enum):
    week = "week"
    month = "month"
    day = "day"


ACCOUNTING_ADMIN_ROLES = {Role.admin.value, Role.accounting.value}
ADMIN_ROLES = {Role.admin.value, Role.accounting.value}
