from fastapi import APIRouter

from app.api.accounts.views import router as accounts_router
from app.api.analytics.views import router as analytics_router


api_router = APIRouter()

api_router.include_router(accounts_router, tags=["accounts"], prefix='/accounts')
api_router.include_router(analytics_router, tags=["analytics"], prefix='/analytics')
