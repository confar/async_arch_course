import asyncio
from typing import NoReturn

from fastapi import APIRouter, Depends, HTTPException, Request, status
from starlette.authentication import requires
from starlette.responses import JSONResponse

from app.api.base_deps import get_database_clients
from app.api.permissions import UserGroups
from app.database import Database

router = APIRouter()


@router.get(
    "/healthcheck",
    status_code=status.HTTP_200_OK,
    description="Healthcheck service",
    name="system:healthcheck",
)
async def healthcheck() -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_200_OK)


@router.get(
    "/readiness-check",
    status_code=status.HTTP_200_OK,
    description="Readiness check service",
    name="system:readiness-check",
)
async def readiness_check(databases: dict[str, Database] = Depends(get_database_clients)) -> JSONResponse:
    db_statuses = await asyncio.gather(*[db.get_status() for db in databases.values()])
    response = {"databases": db_statuses}
    return JSONResponse(response, status_code=status.HTTP_200_OK)


@router.get(
    "/example_permission",
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
@requires(UserGroups.authenticated)
async def example_permission(request: Request) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_200_OK)


@router.get(
    "/unexpected_status_code_example",
    status_code=status.HTTP_418_IM_A_TEAPOT,
    include_in_schema=False,
)
async def unexpected_status_code_example(request: Request) -> NoReturn:
    raise HTTPException(status_code=status.HTTP_418_IM_A_TEAPOT)
