import logging
from dataclasses import dataclass

from app.core.accounts.constants import ACCOUNTING_ADMIN_ROLES, ADMIN_ROLES
from app.core.analytics.repositories import AnalyticsRepository

from app.core.accounts.services import NotSufficientPrivileges

logger = logging.getLogger(__name__)


@dataclass
class AnalyticsService:
    repository: AnalyticsRepository

    async def get_total_sum_earned(self, account) -> int:
        if account.role not in ADMIN_ROLES:
            raise NotSufficientPrivileges()
        cycle_ids = await self.repository.get_cycle_ids_for_today()
        transactions = await self.repository.get_account_transactions_for_cycle_ids(cycle_ids=list(cycle_ids))
        return sum(transaction.delta for transaction in transactions) * -1

    async def get_total_negative_accounts_count(self, account) -> int:
        if account.role not in ADMIN_ROLES:
            raise NotSufficientPrivileges()
        cycle_ids = await self.repository.get_cycle_ids_for_today()
        accounts = await self.repository.get_accounts_with_negative_balance_for_cycle_ids(cycle_ids=list(cycle_ids))
        return len(list(accounts))

    async def get_analytics_data_for_today(self, account):
        if account.role not in ADMIN_ROLES:
            raise NotSufficientPrivileges()
        total_sum = await self.get_total_sum_earned(account)
        negative_accounts_count = await self.get_total_negative_accounts_count(account)
        return total_sum, negative_accounts_count

    async def get_most_expensive_task_cost_for_period(self, account, date_from, date_till):
        if account.role not in ADMIN_ROLES:
            raise NotSufficientPrivileges()
        most_expensive_task_for_period = await self.repository.get_most_expensive_task_cost_for_period(date_from, date_till)
        return most_expensive_task_for_period
