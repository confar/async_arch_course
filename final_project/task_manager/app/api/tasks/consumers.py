import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer

from app.core.tasks.repositories import TaskRepository, TaskEventRepository
from app.core.tasks.services import TaskService
from app.main import get_app

logger = logging.getLogger(__name__)


loop = asyncio.get_event_loop()


async def consume():
    app = get_app()
    consumer = AIOKafkaConsumer(
        'users.registered',
        group_id="my_group",
        bootstrap_servers='localhost:9092',
    )
    await consumer.start()
    task_service = TaskService(repository=TaskRepository(db=app.state.db),
                               event_repository=TaskEventRepository(producer=app.state.event_producer))
    try:
        async for msg in consumer:
            data = json.loads(msg.value)
            if msg.topic == 'users.registered':
                await task_service.create_worker(public_id=data['public_id'], role=data['role'])
    finally:
        pass

loop.run_until_complete(consume())
