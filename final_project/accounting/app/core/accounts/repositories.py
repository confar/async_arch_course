import datetime
import random
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.accounts.constants import Status, PaymentStatus
from app.core.accounts.models import TaskORM
from app.core.accounts.models import TransactionORM, TransactionType, AccountORM, BillingCycleORM, PaymentORM
from app.database import Database


@dataclass
class AccountRepository:
    db: Database

    async def apply_withdrawal_transaction(self, task: TaskORM, account: AccountORM) -> TransactionORM:
        transaction = TransactionORM(type=TransactionType.withdraw.value,
                                     task_id=task.id,
                                     account_id=account.id,
                                     delta=random.randrange(-20, -10),
                                     cycle_id=account.current_billing_cycle_id)
        async with self.db.session() as session:
            session.add(transaction)
            await session.commit()
            await session.refresh(transaction)
        return transaction

    async def apply_deposit_transaction(self, task: TaskORM, account: AccountORM) -> TransactionORM:
        transaction = TransactionORM(type=TransactionType.deposit.value,
                                     task_id=task.id,
                                     account_id=account.id,
                                     delta=task.costs,
                                     cycle_id=account.current_billing_cycle_id)
        async with self.db.session() as session:
            session.add(transaction)
            await session.commit()
            await session.refresh(transaction)
        return transaction

    async def apply_payment_transaction(self, account: AccountORM, payment: PaymentORM) -> TransactionORM:
        transaction = TransactionORM(type=TransactionType.payment.value,
                                     account_id=account.id,
                                     delta=account.balance,
                                     cycle_id=account.current_billing_cycle_id,
                                     payment_id=payment.id)
        async with self.db.session() as session:
            session.add(transaction)
            await session.commit()
            await session.refresh(transaction)
        return transaction

    async def get_task_by_id(self, task_id: str) -> Optional[TaskORM]:
        query = select(TaskORM).filter_by(public_id=task_id)
        async with self.db.session() as session:
            results = await session.execute(query)
            return results.scalar()

    async def get_account_by_id(self, public_id) -> Optional[AccountORM]:
        query = select(AccountORM).filter_by(public_id=public_id)
        async with self.db.session() as session:
            results = await session.execute(query)
            return results.scalar()

    async def create_account(self, public_id: str, role: str, email: str) -> AccountORM:
        cycle = await self.create_billing_cycle()
        account = AccountORM(public_id=public_id, role=role, balance=0, current_billing_cycle_id=cycle.id, email=email)
        async with self.db.session() as session:
            session.add(account)
            await session.commit()
            await session.refresh(account)
        return account

    async def create_billing_cycle(self) -> BillingCycleORM:
        cycle = BillingCycleORM(status=Status.open.value)
        async with self.db.session() as session:
            session.add(cycle)
            await session.commit()
            await session.refresh(cycle)
        return cycle

    async def update_account_billing_cycle(self, account) -> AccountORM:
        cycle = await self.create_billing_cycle()
        account.current_billing_cycle_id = cycle.id
        async with self.db.session() as session:
            session.add(account)
            await session.commit()
            await session.refresh(account)
        return account

    async def create_task(self, public_id: str, description: str) -> TaskORM:
        task = TaskORM(public_id=public_id, description=description, costs=random.randint(20, 40))
        async with self.db.session() as session:
            session.add(task)
            await session.commit()
            await session.refresh(task)
        return task

    async def change_account_balance(self, account: AccountORM, transaction: TransactionORM) -> AccountORM:
        account.balance += transaction.delta
        async with self.db.session() as session:
            session.add(account)
            await session.commit()
            await session.refresh(account)
        return account

    async def reset_account_balance(self, account: AccountORM) -> AccountORM:
        account.balance = 0
        async with self.db.session() as session:
            session.add(account)
            await session.commit()
            await session.refresh(account)
        return account

    async def get_account_transactions_for_cycle_ids(self, cycle_ids: list[int]) -> list[TransactionORM]:
        query = (select(TransactionORM)
                 .filter(TransactionORM.cycle_id.in_(cycle_ids),
                         TransactionORM.type.in_([TransactionType.deposit.value,
                                                  TransactionType.withdraw.value]))
                 .options(joinedload(TransactionORM.task)))
        async with self.db.session() as session:
            results = await session.execute(query)
            return results.scalars()

    async def get_accounts_for_cycle_ids(self, cycle_ids: list[int]) -> list[AccountORM]:
        query = select(AccountORM, BillingCycleORM).filter(AccountORM.current_billing_cycle_id.in_(cycle_ids))
        async with self.db.session() as session:
            results = await session.execute(query)
            return results.scalars()

    async def get_cycle_ids_for_today(self) -> list[int]:
        now = datetime.datetime.now()
        from_dt = datetime.datetime.combine(now, datetime.time.min)
        till_dt = datetime.datetime.combine(now, datetime.time.max)
        query = select(BillingCycleORM.id).filter(BillingCycleORM.created_at >= from_dt,
                                                  BillingCycleORM.created_at <= till_dt)
        async with self.db.session() as session:
            results = await session.execute(query)
            return results.scalars()

    async def get_cycle_by_id(self, cycle_id):
        query = select(BillingCycleORM).filter_by(id=cycle_id)
        async with self.db.session() as session:
            results = await session.execute(query)
            return results.scalar()

    async def close_cycle(self, cycle: BillingCycleORM, payment: Optional[PaymentORM] = None) -> BillingCycleORM:
        cycle.status = Status.closed
        if payment:
            cycle.payment = payment
        async with self.db.session() as session:
            session.add(cycle)
            await session.commit()
            await session.refresh(cycle)
        return cycle

    async def create_payment(self, amount: int) -> PaymentORM:
        payment = PaymentORM(amount=amount, status=PaymentStatus.initiated.value)
        async with self.db.session() as session:
            session.add(payment)
            await session.commit()
            await session.refresh(payment)
        return payment
