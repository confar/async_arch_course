import json
from dataclasses import dataclass

import aiokafka as aiokafka

from task_manager.app.database import Database
from task_manager.app.core.tasks.models import TaskORM, Worker


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

    def get_assignable_workers(self):
        pass

    def assign_task(self, task, assignee: Worker):
        pass


@dataclass
class TaskEventRepository:

    @staticmethod
    def serializer(value):
        return json.dumps(value).encode()

    def produce_assigned_event(self, task_id: int, user_id: int, description: str):
        producer = aiokafka.AIOKafkaProducer(bootstrap_servers='localhost:9092',
                                             value_serializer=self.serializer,
                                             compression_type="gzip")
        await producer.start()
        data = {"task_id": task_id, "user_id": user_id, "description": description}
        try:
            await producer.send_and_wait("tasks_business_events", data)
        finally:
            await producer.stop()

    def produce_mark_done_event(self, task_id: int, user_id: int):
        producer = aiokafka.AIOKafkaProducer(bootstrap_servers='localhost:9092',
                                             value_serializer=self.serializer,
                                             compression_type="gzip")
        await producer.start()
        data = {"task_id": task_id, "user_id": user_id}
        try:
            await producer.send_and_wait("tasks_business_events", data)
        finally:
            await producer.stop()
