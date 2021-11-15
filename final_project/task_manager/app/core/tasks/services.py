import random
from dataclasses import dataclass

from app.core.tasks.models import WorkerORM
from app.core.tasks.repositories import TaskRepository, TaskEventRepository


class TaskNotOwnedError(Exception):
    pass


class NotSufficientPrivileges(Exception):
    pass


@dataclass
class TaskService:
    repository: TaskRepository
    event_repository: TaskEventRepository

    def create_task(self, creator_id: int, description: str, assignee: WorkerORM):
        task = self.repository.create_task(creator_id=creator_id, description=description)
        task = self.repository.assign_task(task, assignee=assignee)
        self.event_repository.produce_assigned_event(task_id=task.id,
                                                     user_id=assignee.user_id,
                                                     description=task.description)
        return task

    def get_all_tasks(self):
        return self.repository.get_all_tasks()

    def get_all_open_tasks(self):
        return self.repository.get_all_open_tasks()
    
    def get_worker_by_id(self, public_id):
        return self.repository.get_worker_by_id(public_id)

    def create_worker(self, public_id, role):
        return self.repository.create_worker(public_id, role)

    def get_user_tasks(self, worker_id: int):
        return self.repository.get_worker_tasks(worker_id=worker_id)

    def get_task_by_id(self, task_id: int):
        return self.repository.get_task_by_id(task_id=task_id)

    def get_assignable_workers(self):
        return self.repository.get_assignable_workers()

    def complete_task(self, worker: WorkerORM, task_id: int):
        task = self.get_task_by_id(task_id)
        if task.creator_id != worker.id:
            raise TaskNotOwnedError()
        task = self.repository.mark_task_complete(task)
        self.event_repository.produce_mark_done_event(task_id=task.id,
                                                      user_id=worker.user_id)
        return task

    def assign_tasks(self, request_worker: WorkerORM):
        if request_worker.role != 'manager':
            raise NotSufficientPrivileges()
        tasks = self.get_all_open_tasks()
        workers = self.get_assignable_workers()
        for task in tasks:
            worker = random.choice(workers)
            self.repository.assign_task(task, assignee=worker)
            self.event_repository.produce_assigned_event(task_id=task.id,
                                                         user_id=worker.user_id,
                                                         description=task.description)
        return None
