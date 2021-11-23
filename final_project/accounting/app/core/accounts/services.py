import logging
from dataclasses import dataclass

from app.core.accounts.constants import ACCOUNTING_ADMIN_ROLES, ADMIN_ROLES
from app.core.accounts.models import TransactionORM, AccountORM, TaskORM
from app.core.accounts.repositories import AccountRepository
from app.emails import send_mail_async


class NotSufficientPrivileges(Exception):
    pass


logger = logging.getLogger(__name__)


@dataclass
class AccountService:
    repository: AccountRepository

    async def process_assigned_task(self, task_id: str, account_id: str) -> TaskORM:
        task = await self.repository.get_task_by_id(task_id)
        account = await self.repository.get_account_by_id(account_id)
        if task and account:
            transaction = await self.repository.apply_withdrawal_transaction(task=task, account=account)
            await self.repository.change_account_balance(account, transaction)
            return task

    async def process_completed_task(self, task_id: str, account_id: str) -> TaskORM:
        task = await self.repository.get_task_by_id(task_id)
        account = await self.repository.get_account_by_id(account_id)
        if task and account:
            transaction = await self.repository.apply_deposit_transaction(task=task, account=account)
            await self.repository.change_account_balance(account, transaction)
            return task

    async def close_billing_cycles(self) -> None:
        cycle_ids = await self.repository.get_cycle_ids_for_today()
        accounts = await self.repository.get_accounts_for_cycle_ids(cycle_ids=list(cycle_ids))
        for account in accounts:
            current_cycle = await self.repository.get_cycle_by_id(cycle_id=account.current_billing_cycle_id)
            if account.balance <= 0:
                await self.repository.update_account_billing_cycle(account)
                await self.repository.close_cycle(cycle=current_cycle)
            else:
                payment = await self.repository.create_payment(amount=account.balance)
                await self.repository.apply_payment_transaction(account=account, payment=payment)
                try:
                    await self.send_payment_email(amount=account.balance, email=account.email)
                except Exception as exc:
                    logger.info('cant send email due to %s', exc)
                await self.repository.close_cycle(cycle=current_cycle, payment=payment)
                await self.repository.reset_account_balance(account)
        return None

    async def get_account_transactions_for_today(self, account: AccountORM) -> list[TransactionORM]:
        cycle_id = account.current_billing_cycle_id
        return await self.repository.get_account_transactions_for_cycle_ids(cycle_ids=[cycle_id])

    async def get_account_by_id(self, public_id):
        return await self.repository.get_account_by_id(public_id)

    async def create_account(self, public_id: str, role: str, email: str):
        return await self.repository.create_account(public_id, role, email)

    async def create_task(self, public_id, description):
        return await self.repository.create_task(public_id, description)

    async def send_payment_email(self, amount, email):
        await send_mail_async('uberpopug@mail.ru',
                              [email],
                              "Payment Received",
                              f'Today you\'ve earned {amount} dollars',
                              textType="plain")

    async def get_total_sum_earned(self, account) -> int:
        if account.role not in ACCOUNTING_ADMIN_ROLES:
            raise NotSufficientPrivileges()
        cycle_ids = await self.repository.get_cycle_ids_for_today()
        cycle_ids = list(cycle_ids)
        transactions = await self.repository.get_account_transactions_for_cycle_ids(cycle_ids)
        return sum(transaction.delta for transaction in transactions) * -1
