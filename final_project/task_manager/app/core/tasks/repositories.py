import json
from typing import Optional
from uuid import UUID

import aiokafka
from aiokafka import AIOKafkaProducer
from dataclasses import dataclass
from sqlalchemy import select

from app.database import Database
from app.core.tasks.models import TaskORM, WorkerORM, ASSIGNABLE_ROLES, StatusEnum


@dataclass
class TaskRepository:
    db: Database

    async def create_task(self, creator_id, description, assignee_id):
        task = TaskORM(creator_id=creator_id, description=description,
                       assignee_id=assignee_id, status=StatusEnum.open.value)
        async with self.db.session() as session:
            session.add(task)
            await session.commit()
            await session.refresh(task)
        return task

    async def get_worker_tasks(self, worker_id):
        query = select(TaskORM).filter_by(assignee_id=worker_id)
        async with self.db.session() as session:
            results = await session.execute(query)
            return results.scalars()

    async def get_task_by_id(self, task_id) -> Optional[TaskORM]:
        query = select(TaskORM).filter_by(id=task_id)
        async with self.db.session() as session:
            results = await session.execute(query)
            return results.scalar()

    async def mark_task_complete(self, task):
        task.status = StatusEnum.done
        async with self.db.session() as session:
            await session.merge(task)
            await session.commit()
            await session.refresh(task)
        return task

    async def get_all_open_tasks(self):
        query = select(TaskORM).filter_by(status=StatusEnum.open)
        async with self.db.session() as session:
            results = await session.execute(query)
            return results.scalars()

    async def get_worker_by_id(self, public_id) -> Optional[WorkerORM]:
        query = select(WorkerORM).filter_by(public_id=public_id)
        async with self.db.session() as session:
            results = await session.execute(query)
            return results.scalar()

    async def create_worker(self, public_id, role):
        worker = WorkerORM(public_id=public_id, role=role)
        async with self.db.session() as session:
            session.add(worker)
            await session.commit()
            await session.refresh(worker)
        return worker

    async def get_assignable_workers(self):
        query = select(WorkerORM).filter(WorkerORM.role.in_(ASSIGNABLE_ROLES),
                                         WorkerORM.id >= 12)
        async with self.db.session() as session:
            results = await session.execute(query)
            return results.scalars()

    async def assign_task(self, task: TaskORM, assignee_id: int):
        task.assignee_id = assignee_id
        async with self.db.session() as session:
            session.add(task)
            await session.commit()
        return task


@dataclass
class TaskEventRepository:
    producer: AIOKafkaProducer

    @staticmethod
    def serializer(value):
        return json.dumps(value).encode()

    async def produce_task_assigned_event(self, task_id: UUID, user_id: str):
        producer = aiokafka.AIOKafkaProducer(bootstrap_servers='localhost:9092',
                                             value_serializer=self.serializer,
                                             compression_type="gzip")
        await producer.start()
        data = {"task_id": task_id.hex, "user_id": user_id}
        try:
            await producer.send_and_wait("tasks.assigned", data)
        finally:
            await producer.stop()

    async def produce_task_completed(self, task_id: UUID, user_id: str):
        producer = aiokafka.AIOKafkaProducer(bootstrap_servers='localhost:9092',
                                             value_serializer=self.serializer,
                                             compression_type="gzip")
        await producer.start()
        data = {"task_id": task_id.hex, "user_id": user_id}
        try:
            await producer.send_and_wait("tasks.completed", data)
        finally:
            await producer.stop()

    async def produce_task_created_event(self, task_id: UUID, description):
        producer = aiokafka.AIOKafkaProducer(bootstrap_servers='localhost:9092',
                                             value_serializer=self.serializer,
                                             compression_type="gzip")
        await producer.start()
        data = {"task_id": task_id.hex, "description": description}
        try:
            await producer.send_and_wait("tasks.created", data)
        finally:
            await producer.stop()
