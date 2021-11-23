import uuid

from sqlalchemy import Column, INTEGER, func, ForeignKey, TEXT, VARCHAR
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, ENUM
from sqlalchemy.ext.declarative import ConcreteBase, declarative_base
from sqlalchemy.orm import relationship

from app.core.accounts.constants import TransactionType, Role, Status

DBBase: ConcreteBase = declarative_base()


class TransactionORM(DBBase):
    __tablename__ = "transactions"

    id = Column(INTEGER(), autoincrement=True, primary_key=True)
    public_id = Column(UUID(as_uuid=True), default=uuid.uuid4)

    account_id = Column(INTEGER(), ForeignKey("accounts.id"))
    task_id = Column(INTEGER(), ForeignKey("tasks.id"))
    cycle_id = Column(ForeignKey('billing_cycles.id'))
    payment_id = Column(ForeignKey('payments.id'), nullable=True)

    delta = Column(INTEGER(), name='Credit/Debit')
    type = Column(ENUM(*TransactionType.display_values(), name='Тип транзакции'))
    created_at = Column(TIMESTAMP, server_default=func.now())

    task = relationship("task", backref="transactions")


class AccountORM(DBBase):
    __tablename__ = "accounts"

    id = Column(INTEGER(), autoincrement=True, primary_key=True)
    public_id = Column(TEXT())
    email = Column(VARCHAR(length=50))
    role = Column(ENUM(*Role.display_values(), name='Role'), doc="Тип роли")
    balance = Column(INTEGER())
    current_billing_cycle_id = Column(ForeignKey('billing_cycles.id'))
    created_at = Column(TIMESTAMP, server_default=func.now())


class TaskORM(DBBase):
    __tablename__ = "tasks"
    id = Column(INTEGER(), autoincrement=True, primary_key=True)
    public_id = Column(TEXT())
    description = Column(TEXT())
    costs = Column(INTEGER())
    created_at = Column(TIMESTAMP, server_default=func.now())


class PaymentORM(DBBase):
    __tablename__ = "payments"
    id = Column(INTEGER(), autoincrement=True, primary_key=True)
    status = Column(ENUM(*Status.display_values(), name='Тип цикла'))
    amount = Column(INTEGER())
    created_at = Column(TIMESTAMP, server_default=func.now())


class BillingCycleORM(DBBase):
    __tablename__ = "billing_cycles"
    id = Column(INTEGER(), autoincrement=True, primary_key=True)
    status = Column(ENUM(*Status.display_values(), name='Тип цикла'))
    payment = Column(ForeignKey('payments.id'), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
