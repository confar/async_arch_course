from dataclasses import dataclass
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from sqlalchemy.exc import NoResultFound
from app.core.users.constants import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.users.repositories import UserRepository, UserEventRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class UserService:
    repository: UserRepository
    event_repository: UserEventRepository

    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def hashed_password(self, plain_password):
        return pwd_context.hash(plain_password)

    async def authenticate_user(self, username: str, password: str):
        try:
            user = await self.repository.get_user(username)
        except NoResultFound:
            user = await self.repository.create_user(username, self.hashed_password(password))
            await self.event_repository.produce_user_registered_event(public_id=user.public_id, role=user.role)
        else:
            if not self.verify_password(password, user.password_hash):
                return False
        return user

    def create_access_token(self, data: dict):
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
