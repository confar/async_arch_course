import json
from dataclasses import dataclass

from aiokafka import AIOKafkaProducer
from sqlalchemy import select

from app.core.users.models import UserORM, RoleEnum
from app.database import Database


@dataclass
class UserRepository:
    db: Database

    async def get_user(self, username: str) -> UserORM:
        query = select(UserORM).filter_by(email=username)
        async with self.db.session() as session:
            results = await session.execute(query)
            return results.scalar_one()

    async def create_user(self, username: str, password: str) -> UserORM:
        async with self.db.session() as session:
            user = UserORM(email=username, role=RoleEnum.worker.value, password_hash=password)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user


@dataclass
class UserEventRepository:
    producer: AIOKafkaProducer

    async def produce_user_registered_event(self, public_id: str, role: RoleEnum):
        await self.producer.start()
        data = {"public_id": public_id, "role": role.value}
        try:
            await self.producer.send_and_wait("users.registered", data)
        finally:
            await self.producer.stop()
