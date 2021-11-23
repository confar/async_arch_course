from aiokafka import AIOKafkaProducer

from app.core.analytics.repositories import AnalyticsRepository
from app.core.analytics.services import AnalyticsService
from app.database import Database
from starlette.requests import Request


def get_db_client(request: Request) -> Database:
    return request.app.state.db


def get_kafka_client(request: Request) -> AIOKafkaProducer:
    return request.app.state.event_producer

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from starlette import status

from app.api.base_deps import get_db_client
from app.api.base_deps import get_kafka_client
from app.core.accounts.repositories import AccountRepository, AccountEventRepository
from app.core.accounts.services import AccountService
from app.database import Database

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_account_repository(
        db: Database = Depends(get_db_client, use_cache=True),
) -> AccountRepository:
    return AccountRepository(db=db)


def get_account_service(
        repository: AccountRepository = Depends(get_account_repository, use_cache=True),
) -> AccountService:
    return AccountService(repository=repository)


def get_analytics_repository(
        db: Database = Depends(get_db_client, use_cache=True),
) -> AnalyticsRepository:
    return AnalyticsRepository(db=db)


def get_analytics_service(
        repository: AnalyticsRepository = Depends(get_analytics_repository, use_cache=True),
) -> AnalyticsService:
    return AnalyticsService(repository=repository)


async def get_current_account(token: str = Depends(oauth2_scheme),
                             account_service=Depends(get_account_service)):
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
    account = await account_service.get_account_by_id(public_id=public_id)
    if account is None:
        raise credentials_exception
    return account
