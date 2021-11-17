from aiokafka import AIOKafkaProducer
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from jose import JWTError, jwt
from app.api.base_deps import get_db_client, get_kafka_client
from app.api.users.serializers import TokenData, User
from app.core.users.constants import SECRET_KEY, ALGORITHM
from app.core.users.repositories import UserRepository, UserEventRepository
from app.core.users.services import UserService
from app.database import Database

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user_repository(
        db: Database = Depends(get_db_client, use_cache=True),
) -> UserRepository:
    return UserRepository(db=db)


def get_user_event_repository(
    message_broker: AIOKafkaProducer = Depends(get_kafka_client, use_cache=True)
) -> UserEventRepository:
    return UserEventRepository(producer=message_broker)


def get_user_service(
        repository: UserRepository = Depends(get_user_repository, use_cache=True),
        event_repository: UserEventRepository = Depends(get_user_event_repository, use_cache=True),
) -> UserService:
    return UserService(repository=repository, event_repository=event_repository)


async def get_current_user(token: str = Depends(oauth2_scheme),
                           user_service=Depends(get_user_service)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid: str = payload.get("public_id")
        if user_uuid is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = user_service.get_user_by_public_id(public_id=user_uuid)
    if user is None:
        raise credentials_exception
    return user


