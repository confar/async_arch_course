import json

from aiokafka import AIOKafkaConsumer
import asyncio

from app.api.rest.tasks.deps import get_task_service
from app.core.tasks.repositories import TaskRepository, TaskEventRepository
from app.main import get_app


async def registered_users_consume():
    consumer = AIOKafkaConsumer(
        'users.registered',
        bootstrap_servers='localhost:9092')
    app = get_app()
    task_service = get_task_service(repository=TaskRepository(db=app.state.db),
                                    event_repository=TaskEventRepository(producer=app.state.event_producer))
    await consumer.start()
    try:
        async for msg in consumer:
            data = json.loads(msg.value)
            await task_service.create_worker(public_id=data['public_id'], role=data['role'])
            print("consumed: ", msg.topic, msg.partition, msg.offset,
                  msg.key, msg.value, msg.timestamp)
    finally:
        await consumer.stop()

asyncio.run(registered_users_consume())
