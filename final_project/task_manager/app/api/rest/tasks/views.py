from datetime import timedelta

from fastapi import Depends, HTTPException, status, APIRouter

from app.api.rest.tasks.deps import get_task_service, get_current_active_user
from app.api.rest.tasks.serializers import Token, User

router = APIRouter()


@router.post("/tasks/assign", response_model=Token)
async def assign_tasks(user=Depends(get_current_active_user),
                      task_service=Depends(get_task_service)):
    user = task_service.assign_tasks(request_worker=user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {}


@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
