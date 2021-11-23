import aiocron
import asyncio

from app.core.accounts.repositories import AccountRepository
from app.core.accounts.services import AccountService
from main import get_app


@aiocron.crontab('0 0 * * *')
async def close_billing_cycles():
    app = get_app()
    account_service = AccountService(repository=AccountRepository(db=app.state.db))
    await account_service.close_billing_cycles()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.get_event_loop().run_forever()
