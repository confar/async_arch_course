from fastapi import Depends

from app.api.base_deps import get_dbl_client
from app.core.user_account.repositories import UserAccountRepository
from app.core.user_account.services import UserAccountService
from app.database import Database


def get_user_account_repository(
    dbl: Database = Depends(get_dbl_client, use_cache=True),
) -> UserAccountRepository:
    return UserAccountRepository(dbl=dbl)


def get_user_account_service(
    repository: UserAccountRepository = Depends(get_user_account_repository, use_cache=True),
) -> UserAccountService:
    return UserAccountService(repository=repository)
