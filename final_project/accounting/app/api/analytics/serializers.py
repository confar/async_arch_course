import datetime

from pydantic import BaseModel, Field
from pydantic.schema import date


class UserSerializer(BaseModel):
    public_id: str
    role: str
    id: int

    class Config:
        orm_mode = True


class AnalyticsDashboardSerializer(BaseModel):
    total_sum_earned: int
    negative_balance_popugs_count: int


class MostExpensiveTaskSerializer(BaseModel):
    date_from: date
    date_till: date
    costs: int = Field(..., title="id юзера на которого засайнить задачу.")