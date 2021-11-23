import datetime
from pydantic import BaseModel, Field


class UserSerializer(BaseModel):
    public_id: str
    role: str
    id: int
    email: str

    class Config:
        orm_mode = True


class TaskSerializer(BaseModel):
    public_id: str
    description: str
    costs: int

    class Config:
        orm_mode = True


class TransactionSerializer(BaseModel):
    type: str
    delta: str
    task: TaskSerializer
    id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True
