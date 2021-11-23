import datetime
from dataclasses import dataclass

from sqlalchemy import select, func

from app.core.accounts.models import TransactionORM, TransactionType, AccountORM, BillingCycleORM
from app.database import Database


@dataclass
class AnalyticsRepository:
    db: Database

    async def get_account_transactions_for_cycle_ids(self, cycle_ids: list[int]) -> list[TransactionORM]:
        query = select(TransactionORM).filter(TransactionORM.cycle_id.in_(cycle_ids),
                                              TransactionORM.type.in_([TransactionType.deposit.value,
                                                                       TransactionType.withdraw.value]))
        async with self.db.session() as session:
            results = await session.execute(query)
            return results.scalars()

    async def get_accounts_with_negative_balance_for_cycle_ids(self, cycle_ids: list[int]) -> list[AccountORM]:
        query = select(AccountORM).filter(AccountORM.current_billing_cycle_id.in_(cycle_ids),
                                          AccountORM.balance < 0)
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

    async def get_most_expensive_task_cost_for_period(self, date_from, date_till) -> int:
        date_from = datetime.datetime.combine(date_from, datetime.time.min)
        date_till = datetime.datetime.combine(date_till, datetime.time.max)
        query = select(func.max(TransactionORM.delta)).filter(TransactionORM.type == TransactionType.deposit.value,
                                                              TransactionORM.created_at >= date_from,
                                                              TransactionORM.created_at <= date_till)
        async with self.db.session() as session:
            results = await session.execute(query)
            return results.scalar()

