from app.api.rest.base_deps import get_db_client
from app.api.rest.tasks.serializers import User

from app.api.rest.base_deps import get_kafka_client
from app.core.tasks.services import TaskService
from app.database import Database
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from starlette import status

from app.core.tasks.repositories import TaskRepository, TaskEventRepository

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_task_repository(
        db: Database = Depends(get_db_client, use_cache=True),
) -> TaskRepository:
    return TaskRepository(db=db)


def get_task_event_repository(
    message_broker: Depends(get_kafka_client, use_cache=True)
):
    return TaskEventRepository(producer=message_broker)


def get_task_service(
        repository: TaskRepository = Depends(get_task_repository, use_cache=True),
        event_repository: TaskEventRepository = Depends(get_task_repository, use_cache=True),
) -> TaskService:
    return TaskService(repository=repository, event_repository=event_repository)


async def get_current_user(token: str = Depends(oauth2_scheme),
                           task_service=Depends(get_task_service)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        public_id: str = payload.get("public_id")
        if public_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    worker = task_service.get_worker(public_id=public_id)
    if worker is None:
        raise credentials_exception
    return worker


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user