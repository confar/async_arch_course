from typing import Optional

from app.core.user_account.models import User, UserProfile
from app.core.user_account.repositories import UserAccountRepository
from dataclasses import dataclass


@dataclass
class UserAccountService:
    repository: UserAccountRepository

    async def get_user_by_sid(self, sid: str) -> Optional[User]:
        return await self.repository.get_user_by_sid(sid)

    async def get_account_data(self, user_id: int) -> User:
        account_info = await self.repository.fetch_full_account_info(user_id=user_id)
        return account_info

    async def get_profile(self, user_id: int) -> UserProfile:
        account_info = await self.repository.get_profile(user_id=user_id)
        return account_info
