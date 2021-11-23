import json
from dataclasses import dataclass
from uuid import UUID

import aiokafka
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

    async def get_user_by_public_id(self, public_id: str):
        query = select(UserORM).filter_by(public_id=public_id)
        async with self.db.session() as session:
            results = await session.execute(query)
            return results.scalar_one()


@dataclass
class UserEventRepository:
    producer: AIOKafkaProducer

    @staticmethod
    def serializer(value):
        return json.dumps(value).encode()

    async def produce_user_registered_event(self, public_id: UUID, role: str, email: str):
        producer = aiokafka.AIOKafkaProducer(bootstrap_servers='localhost:9092',
                                             value_serializer=self.serializer,
                                             compression_type="gzip")
        await producer.start()
        data = {"user_id": public_id.hex, "role": role, "email": email}
        try:
            await producer.send_and_wait("users.created", data)
        finally:
            await producer.stop()
