import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.core.user_account.factories import UserFactory

pytestmark = [
    pytest.mark.asyncio,
]


async def test_get_healthcheck(sync_dbl: Session, rest_client: AsyncClient) -> None:
    response = await rest_client.get("/api/healthcheck")
    assert response.status_code == 200


async def test_get_docs(rest_client: AsyncClient) -> None:
    response = await rest_client.get("/openapi.json")
    assert response.status_code == 200


async def test_get_readiness_check(rest_client: AsyncClient) -> None:
    response = await rest_client.get("/api/readiness-check")
    assert response.status_code == 200
    assert response.json() == {
        "databases": [
            {
                "name": "dbl",
                "status": "ready",
            },
            {
                "name": "dbh",
                "status": "ready",
            },
        ],
    }


async def test_example_permission_success(sync_dbl: Session, rest_client: AsyncClient) -> None:
    user = UserFactory()

    response = await rest_client.get(f"/api/example_permission", cookies={"SID": user.session.sid})

    assert response.status_code == 200


async def test_example_permission_forbidden(sync_dbl: Session, rest_client: AsyncClient) -> None:
    response = await rest_client.get(f"/api/example_permission")

    assert response.status_code == 403
    assert response.json() == {
        "status": 403,
        "error": {"type": "PermissionMissing", "title": "Permission required for this endpoint is missing"},
    }


async def test_unknown_endpoint_exception(sync_dbl: Session, rest_client: AsyncClient) -> None:
    response = await rest_client.get(f"/example_permission")

    assert response.status_code == 404
    assert response.json() == {
        "status": 404,
        "error": {"type": "UnknownEndpoint", "title": "Requested endpoint does not exist"},
    }


async def test_exception_even_when_status_is_unexpected(sync_dbl: Session, rest_client: AsyncClient) -> None:
    response = await rest_client.get(f"/api/unexpected_status_code_example")

    assert response.status_code == 418
    assert response.json() == {"status": 418}
