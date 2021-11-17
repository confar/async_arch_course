import random
from dataclasses import dataclass

from app.core.tasks.models import WorkerORM, RoleEnum, ADMIN_ROLES, TaskORM
from app.core.tasks.repositories import TaskRepository, TaskEventRepository


class TaskNotOwnedError(Exception):
    pass


class NotSufficientPrivileges(Exception):
    pass


@dataclass
class TaskService:
    repository: TaskRepository
    event_repository: TaskEventRepository

    async def create_task(self, creator_id: int, description: str, assignee: WorkerORM):
        task = await self.repository.create_task(creator_id=creator_id, description=description, assignee_id=assignee)
        await self.event_repository.produce_task_created_event(task_id=task.id,
                                                               user_id=assignee.public_id,
                                                               description=task.description)
        await self.event_repository.produce_task_assigned_event(task_id=task.id,
                                                                user_id=task.public_id,
                                                                description=task.description)
        return task

    async def get_user_tasks(self, worker_id: int):
        return await self.repository.get_worker_tasks(worker_id=worker_id)

    async def get_task_by_id(self, task_id: int):
        return await self.repository.get_task_by_id(task_id=task_id)

    async def complete_task(self, worker: WorkerORM, task: TaskORM):
        if task.creator_id != worker.id:
            raise TaskNotOwnedError()
        task = await self.repository.mark_task_complete(task)
        await self.event_repository.produce_task_completed(task_id=task.id,
                                                           user_id=task.assignee_id)
        return task

    async def assign_tasks(self, request_user: WorkerORM):
        if request_user.role not in ADMIN_ROLES:
            raise NotSufficientPrivileges()
        tasks = await self.repository.get_all_open_tasks()
        workers = await self.repository.get_assignable_workers()
        for task in tasks:
            worker = random.choice(workers)
            task = await self.repository.assign_task(task, assignee_id=worker.id)
            await self.event_repository.produce_task_assigned_event(task_id=task.id,
                                                                    user_id=task.assignee_id,
                                                                    description=task.description)
        return None

    async def get_worker_by_id(self, public_id):
        return await self.repository.get_worker_by_id(public_id)

    async def create_worker(self, public_id, role):
        return await self.repository.create_worker(public_id, role)