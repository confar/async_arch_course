from fastapi import APIRouter, Depends, Request, status
from starlette.authentication import requires
from starlette.status import HTTP_200_OK

from app.api.exceptions import (
    PermissionMissingError,
    RequestParamValidationError,
    include_exception_responses,
)
from app.api.permissions import UserGroups
from app.api.user_account.deps import get_user_account_service
from app.api.user_account.serializers import (
    UserAccount,
    UserAccountResponseSerializer,
    UserAccountSerializer,
    UserProfileWriteSerializer,
)
from app.core.user_account.models import User
from app.core.user_account.services import UserAccountService

router = APIRouter()


@router.get(
    "/account/me",
    response_model=UserAccountResponseSerializer,
    responses=include_exception_responses(PermissionMissingError),
    name="account:get_user",
    status_code=HTTP_200_OK,
)
@requires(UserGroups.authenticated)
async def get_user_detailed_info(
    request: Request,
    user_service: UserAccountService = Depends(get_user_account_service),
) -> UserAccountResponseSerializer:
    user: User = await user_service.get_account_data(request.user.id)
    user_data = UserAccount.from_orm(user)

    return UserAccountResponseSerializer(status=status.HTTP_200_OK, payload=UserAccountSerializer(data=user_data))

