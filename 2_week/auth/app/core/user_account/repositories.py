from typing import Optional

from app.core.user_account.models import (
    User,
    UserProfile,
    UserSession,
)
from app.database import Database
from dataclasses import dataclass
from sqlalchemy import and_, select
from sqlalchemy.orm import joinedload


@dataclass
class UserAccountRepository:
    dbl: Database

    async def get_user_by_sid(self, sid: str) -> Optional[User]:
        query = select(User).join(
            UserSession,
            and_(
                UserSession.sid == sid,
                UserSession.user_id == User.id,
            ),
        )
        async with self.dbl.session() as session:
            user = await session.execute(query)
            return user.scalar()

    async def fetch_full_account_info(self, user_id: int) -> User:
        query = (
            select(User)
            .options(
                joinedload(User.profile),
                joinedload(User.phone),
                joinedload(User.groups),
            )
            .filter_by(
                id=user_id,
            )
        )

        async with self.dbl.session() as session:
            profile = await session.execute(query)
            return profile.scalar()

    async def get_profile(self, user_id: int) -> UserProfile:
        query = select(UserProfile).filter_by(
            user_id=user_id,
        )

        async with self.dbl.session() as session:
            profile = await session.execute(query)
            return profile.scalar()

    async def save_profile(self, profile: UserProfile) -> None:
        async with self.dbl.session() as session:
            await session.merge(profile)
            await session.commit()
