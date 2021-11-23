from typing import Optional

from pydantic import BaseModel, Field
from pydantic.types import UUID


class UserSerializer(BaseModel):
    public_id: str
    role: str
    id: int

    class Config:
        orm_mode = True


class TaskSerializer(BaseModel):
    public_id: UUID
    status: str
    assignee_id: int
    creator_id: int
    description: str
    id: int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class AddTaskSerializer(BaseModel):
    assignee_id: str = Field(..., title="публичный id юзера на которого засайнить задачу.")
    description: str = Field(..., title="Описание задачи")
