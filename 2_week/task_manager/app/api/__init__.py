from fastapi import APIRouter

from app.api.collections.views import router as collections_router
from app.api.reviews.views import router as reviews_router
from app.api.system.views import router as system_router
from app.api.user_account.views import router as account_router

api_router = APIRouter()

api_router.include_router(collections_router, tags=["collections"])
api_router.include_router(reviews_router, tags=["reviews"])
api_router.include_router(account_router, tags=["user_account"])
api_router.include_router(system_router, tags=["system"])
