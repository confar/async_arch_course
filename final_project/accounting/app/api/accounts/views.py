from fastapi import Depends, APIRouter

from app.api.accounts.serializers import UserSerializer, TaskSerializer, TransactionSerializer
from app.api.base_deps import get_current_account, get_account_service

router = APIRouter()


@router.get("/my-transactions/", response_model=list[TransactionSerializer])
async def get_my_transaction_log(account=Depends(get_current_account),
                                 account_service=Depends(get_account_service)):
    transactions = await account_service.get_account_transactions_for_today(account=account)
    return list(transactions)


@router.get("/total-earned/")
async def get_total_earned_data(account=Depends(get_current_account),
                                account_service=Depends(get_account_service)):
    sum_for_today = await account_service.get_total_sum_earned(account=account)
    return sum_for_today


@router.get("/me/", response_model=UserSerializer)
async def read_users_me(current_user: UserSerializer = Depends(get_current_account)):
    return current_user

