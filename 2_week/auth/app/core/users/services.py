from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

from auth.app.core.users.constants import SECRET_KEY, ALGORITHM
from auth.app.core.users.repositories import UserRepository
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class UserService:
    repository: UserRepository

    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)
    
    def authenticate_user(self, username: str, password: str):
        user = self.repository.get_user(username)
        if not user:
            return False
        if not self.verify_password(password, user.hashed_password):
            return False
        return user

    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt