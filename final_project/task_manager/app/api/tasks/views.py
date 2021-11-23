from fastapi import Depends, HTTPException, status, APIRouter

from app.api.tasks.deps import get_task_service, get_current_user, get_task_or_404
from app.api.tasks.serializers import UserSerializer, TaskSerializer, AddTaskSerializer
from app.core.tasks.services import TaskNotOwnedError, NotSufficientPrivileges

router = APIRouter()


@router.post("/tasks/assign/", response_model=None)
async def assign_tasks(user=Depends(get_current_user),
                       task_service=Depends(get_task_service)):
    try:
        await task_service.assign_tasks(request_user=user)
    except NotSufficientPrivileges:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cant assign tasks",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        return status.HTTP_200_OK


@router.post("/tasks/", response_model=TaskSerializer)
async def create_task(body: AddTaskSerializer,
                      user=Depends(get_current_user),
                      task_service=Depends(get_task_service)):
    task = await task_service.create_task(creator_id=user.id, description=body.description,
                                          assignee_id=body.assignee_id, title=body.title, jira_id=body.jira_id)
    return task


@router.get("/my-tasks/", response_model=list[TaskSerializer])
async def get_my_tasks(user=Depends(get_current_user),
                       task_service=Depends(get_task_service)):
    tasks = await task_service.get_user_tasks(worker_id=user.id)
    return list(tasks)


@router.put("/my-tasks/{task_id}/mark-done/", response_model=TaskSerializer)
async def mark_task_done(user=Depends(get_current_user),
                         task=Depends(get_task_or_404),
                         task_service=Depends(get_task_service)):
    try:
        task = await task_service.complete_task(worker=user, task=task)
    except (TaskNotOwnedError, TaskNotOpenError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cant finish other user's task",
        )
    return task


@router.get("/workers/me/", response_model=UserSerializer)
async def read_users_me(current_user: UserSerializer = Depends(get_current_user)):
    return current_user

