import random
from dataclasses import dataclass

from app.core.tasks.models import WorkerORM, RoleEnum, ADMIN_ROLES, TaskORM, StatusEnum
from app.core.tasks.repositories import TaskRepository, TaskEventRepository


class TaskNotOwnedError(Exception):
    pass


class NotSufficientPrivileges(Exception):
    pass


class TaskNotOpenError(Exception):
    pass


class CantAssignAdminsError(Exception):
    pass


@dataclass
class TaskService:
    repository: TaskRepository
    event_repository: TaskEventRepository

    async def create_task(self, creator_id: int, description: str, assignee_id: str, title: str, jira_id: str):
        assignee = await self.repository.get_worker_by_id(assignee_id)
        if assignee in ADMIN_ROLES:
            raise CantAssignAdminsError()
        task = await self.repository.create_task(creator_id=creator_id, description=description,
                                                 assignee_id=assignee.id, title=title, jira_id=jira_id)
        await self.event_repository.produce_task_created_event(task_id=task.public_id,
                                                               description=task.description,
                                                               title=task.title, jira_id=task.jira_id)
        await self.event_repository.produce_task_assigned_event(task_id=task.public_id,
                                                                user_id=assignee.public_id)
        return task

    async def get_user_tasks(self, worker_id: int):
        return await self.repository.get_worker_tasks(worker_id=worker_id)

    async def get_task_by_id(self, task_id: int):
        return await self.repository.get_task_by_id(task_id=task_id)

    async def complete_task(self, worker: WorkerORM, task: TaskORM):
        if task.status != StatusEnum.open:
            raise TaskNotOpenError()
        if task.assignee_id != worker.id:
            raise TaskNotOwnedError()
        task = await self.repository.mark_task_complete(task)
        await self.event_repository.produce_task_completed(task_id=task.public_id,
                                                           user_id=worker.public_id)
        return task

    async def assign_tasks(self, request_user: WorkerORM):
        if request_user.role not in ADMIN_ROLES:
            raise NotSufficientPrivileges()
        tasks = await self.repository.get_all_open_tasks()
        workers = await self.repository.get_assignable_workers()
        tasks = list(tasks)
        workers = list(workers)
        for task in tasks:
            worker = random.choice(workers)
            task = await self.repository.assign_task(task, assignee_id=worker.id)
            await self.event_repository.produce_task_assigned_event(task_id=task.public_id,
                                                                    user_id=worker.public_id)
        return None

    async def get_worker_by_id(self, public_id):
        return await self.repository.get_worker_by_id(public_id)

    async def create_worker(self, public_id, role):
        return await self.repository.create_worker(public_id, role)