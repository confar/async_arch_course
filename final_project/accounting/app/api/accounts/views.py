from fastapi import APIRouter

router = APIRouter()


@router.post("/token", response_model=None)
async def assign_task():
    pass
