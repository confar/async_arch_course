import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer

from app.core.accounts.repositories import AccountRepository
from app.core.accounts.services import AccountService
from main import get_app

logger = logging.getLogger(__name__)


loop = asyncio.get_event_loop()


async def consume():
    app = get_app()
    consumer = AIOKafkaConsumer(
        'users.created', 'tasks.assigned', 'tasks.completed', 'tasks.created',
        group_id="my_group1",
        bootstrap_servers='localhost:9092',
    )
    # если assigned раньше чем tasks.created, то либо пустой таск, либо ретрай события created
    await consumer.start()
    account_service = AccountService(repository=AccountRepository(db=app.state.db))
    try:
        async for msg in consumer:
            data = json.loads(msg.value)
            if msg.topic == 'users.created':
                await account_service.create_account(public_id=data['user_id'], role=data['role'], email=data['email'])
            elif msg.topic == 'tasks.created':
                await account_service.create_task(public_id=data['task_id'], description=data['description'],
                                                  title=data.get('title'), jira_id=data.get('jira_id'))
            elif msg.topic == 'tasks.assigned':
                await account_service.process_assigned_task(task_id=data['task_id'], account_id=data['user_id'])
            elif msg.topic == 'tasks.completed':
                await account_service.process_completed_task(task_id=data['task_id'], account_id=data['user_id'])
    finally:
        pass

if __name__ == '__main__':
    loop.run_until_complete(consume())
