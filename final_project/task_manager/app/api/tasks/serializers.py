from typing import Optional

from pydantic import BaseModel, Field


class UserSerializer(BaseModel):
    public_id: str
    role: str
    id: int

    class Config:
        orm_mode = True


class TaskSerializer(BaseModel):
    public_id: str
    status: str
    assignee_id: int
    creator_id: int
    description_id: str
    id: int

    class Config:
        orm_mode = True


class AddTaskSerializer(BaseModel):
    assignee_id: int = Field(..., title="id юзера на которого засайнить задачу.")
    description: int = Field(..., title="Описание задачи")