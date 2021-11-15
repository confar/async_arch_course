import json

from aiokafka import AIOKafkaProducer
from dataclasses import dataclass

import aiokafka as aiokafka

from app.database import Database
from app.core.tasks.models import TaskORM, WorkerORM


@dataclass
class TaskRepository:
    db: Database

    def create_task(self, creator_id, description):
        with self.db.session() as session:
            return TaskORM()

    def get_all_tasks(self):
        pass

    def get_worker_tasks(self, worker_id):
        pass

    def get_task_by_id(self, task_id):
        pass

    def mark_task_complete(self, task):
        pass

    def get_all_open_tasks(self):
        pass

    def get_worker_by_id(self):
        pass
    
    async def create_worker(self, public_id, role):
        worker = WorkerORM(public=public_id, role=role)
        async with self.db.session() as session:
            session.add(worker)
            await session.commit()
            await session.refresh(worker)
        return worker

    def get_assignable_workers(self):
        pass

    def assign_task(self, task, assignee: WorkerORM):
        pass


@dataclass
class TaskEventRepository:
    producer: AIOKafkaProducer

    @staticmethod
    def serializer(value):
        return json.dumps(value).encode()

    async def produce_assigned_event(self, task_id: int, user_id: int, description: str):
        await self.producer.start()
        data = {"task_id": task_id, "user_id": user_id, "description": description}
        try:
            await self.producer.send_and_wait("tasks_business_events", data)
        finally:
            await self.producer.stop()

    async def produce_mark_done_event(self, task_id: int, user_id: int):
        await self.producer.start()
        data = {"task_id": task_id, "user_id": user_id}
        try:
            await self.producer.send_and_wait("tasks_business_events", data)
        finally:
            await self.producer.stop()
