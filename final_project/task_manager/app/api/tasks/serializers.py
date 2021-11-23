from typing import Optional, Any

from pydantic import BaseModel, Field, validator
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
    title: str = Field(..., title="Название задачи")
    jira_id: Optional[str] = Field(..., title="Номер задачи в джира")

    @validator("title", always=True)
    def validate_title_doesnt_contain_jira_id(cls, _: int, values: dict[str, Any]) -> str:
        if set(values["title"]) & {']', '['}:
            raise ValueError()
        return values["title"]
