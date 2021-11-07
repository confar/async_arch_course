from dataclasses import dataclass

from auth.app.api.users.serializers import User
from auth.app.database import Database


@dataclass
class UserRepository:
    db: Database

    def get_user(self, username: str) -> UserORM:
        with self.db.session() as session:
            return User()
