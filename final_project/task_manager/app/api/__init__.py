from fastapi import APIRouter

from app.api.tasks.views import router as tasks_router

api_router = APIRouter()

api_router.include_router(tasks_router, tags=["tasks"])