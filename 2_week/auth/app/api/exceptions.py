from enum import Enum
from typing import Any, Optional, Type

from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.base_schemas import BaseError, BaseResponse


class ResourceType(str, Enum):
    art = "art"
    collections = "collections"
    review = "review"


class BaseAPIException(Exception):
    _content_type: str = "application/json"
    model: Type[BaseResponse] = BaseResponse
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    title: Optional[str] = None
    type: Optional[str] = None
    detail: Optional[str] = None
    instance: Optional[str] = None

    def __init__(self, **ctx: Any) -> None:
        self.__dict__ = ctx

    def get_response_data(self) -> BaseResponse:
        return self.model(
            status=self.status_code,
            error=self.model.__fields__["error"].type_(
                type=self._get_type_error(),
                detail=self.detail,
                title=self.title,
                instance=self.instance,
            ),
        )

    def _get_type_error(self) -> str:
        return self.model.__fields__["error"].type_.__name__

    @classmethod
    def response_model(cls) -> dict[int, Any]:
        return {
            cls.status_code: {
                "model": cls.model,
                "content": {
                    cls._content_type: cls.model.Config.schema_extra,
                },
            },
        }


class ValidationErrorDescription(BaseModel):
    loc: list[str] = Field(title="The location of the error", example='["path","art_id"]')
    msg: str = Field(title="Human-readable description", example="value is not a valid integer")
    type: str = Field(title="Machine-readable description", example="type_error.integer")


class ParamValidationError(BaseError):
    error_descriptions: Optional[list[ValidationErrorDescription]] = Field(title="List of validation errors ")


class ParamValidationErrorResponse(BaseResponse):
    error: ParamValidationError

    class Config:
        schema_extra = {
            "example": {
                "status": 422,
                "error": {
                    "type": "ParamValidationError",
                    "title": "Validation error because of request parameters",
                    "detail": "Received a validation error while interpreting request parameters. "
                    "See error_descriptions for details",
                    "error_descriptions": [
                        {
                            "loc": ["path", "art_id"],
                            "msg": "value is not a valid integer",
                            "type": "type_error.integer",
                        },
                    ],
                },
            },
        }


class RequestParamValidationError(BaseAPIException):
    model = ParamValidationErrorResponse
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    title = "Validation error because of request parameters"
    detail = "Received a validation error while interpreting request parameters. See error_descriptions for details"

    def get_response_data(self) -> BaseResponse:
        return self.model(
            status=self.status_code,
            error=self.model.__fields__["error"].type_(
                type=self._get_type_error(),
                title=self.title,
                detail=self.detail,
                instance=self.instance,
            ),
        )


class ResourceNotFoundByID(BaseError):
    resource_type: Optional[ResourceType] = Field(title="Type of the resource the server could not find")
    resource_id: Optional[Any] = Field(title="Identifier of the resource the server could not find")


class ResourceNotFoundByIDResponse(BaseResponse):
    error: ResourceNotFoundByID

    class Config:
        schema_extra = {
            "example": {
                "status": 404,
                "error": {
                    "type": "ResourceNotFoundByID",
                    "title": "Resource not found",
                    "detail": "Could not find collections with [123] as an identifier",
                    "resource_type": "collections",
                    "resource_id": [
                        123,
                    ],
                },
            },
        }


class UnknownEndpoint(BaseError):
    pass


class PermissionMissing(BaseError):
    pass


class BadEndpointUsage(BaseError):
    pass


class UnknownEndpointResponse(BaseResponse):
    error: UnknownEndpoint

    class Config:
        schema_extra = {
            "example": {
                "status": 404,
                "error": {
                    "type": "UnknownEndpoint",
                    "title": "Requested endpoint does not exist",
                },
            },
        }


class PermissionMissingResponse(BaseResponse):
    error: PermissionMissing

    class Config:
        schema_extra = {
            "example": {
                "status": 403,
                "error": {
                    "type": "PermissionMissing",
                    "title": "Permission required for this endpoint is missing",
                },
            },
        }


class BadEndpointUsageResponse(BaseResponse):
    error: BadEndpointUsage

    class Config:
        schema_extra = {
            "example": {
                "status": 400,
                "error": {
                    "type": "BadEndpointUsage",
                    "title": "Endpoint was used in the wrong way",
                    "detail": "User cannot add like to their own review",
                },
            },
        }


class ResourceNotFoundByIDError(BaseAPIException):
    model = ResourceNotFoundByIDResponse
    status_code = status.HTTP_404_NOT_FOUND
    detail: str = "Could not find {resource_type} with {resource_id} as an identifier"
    title: str = "Resource not found"
    resource_id: int
    resource_type: ResourceType

    def get_response_data(self) -> BaseResponse:
        return self.model(
            status=self.status_code,
            error=self.model.__fields__["error"].type_(
                type=self._get_type_error(),
                title=self.title,
                detail=self.detail.format(**self.__dict__),
                instance=self.instance,
                resource_type=self.resource_type,
                resource_id=self.resource_id,
            ),
        )


class UnknownEndpointError(BaseAPIException):
    model = UnknownEndpointResponse
    status_code = status.HTTP_404_NOT_FOUND
    title: str = "Requested endpoint does not exist"

    def get_response_data(self) -> BaseResponse:
        return self.model(
            status=self.status_code,
            error=self.model.__fields__["error"].type_(
                type=self._get_type_error(),
                title=self.title,
                detail=self.detail,
            ),
        )


class BadEndpointUsageError(BaseAPIException):
    model = BadEndpointUsageResponse
    status_code = status.HTTP_400_BAD_REQUEST
    title: str = "Endpoint was used in the wrong way"

    def get_response_data(self) -> BaseResponse:
        return self.model(
            status=self.status_code,
            error=self.model.__fields__["error"].type_(
                type=self._get_type_error(),
                title=self.title,
                detail=self.detail,
            ),
        )


class PermissionMissingError(BaseAPIException):
    model = PermissionMissingResponse
    status_code = status.HTTP_403_FORBIDDEN
    title: str = "Permission required for this endpoint is missing"

    def get_response_data(self) -> BaseResponse:
        return self.model(
            status=self.status_code,
            error=self.model.__fields__["error"].type_(
                type=self._get_type_error(),
                title=self.title,
            ),
        )


async def on_api_exception(_: Request, exception: BaseAPIException) -> JSONResponse:
    return JSONResponse(
        status_code=exception.status_code,
        content=exception.get_response_data().dict(exclude_none=True, exclude_unset=True, exclude_defaults=True),
    )


async def generic_http_exception_handler(_: Request, exception: StarletteHTTPException) -> JSONResponse:
    corresponding_api_exceptions: dict[int, BaseAPIException] = {
        UnknownEndpointError.status_code: UnknownEndpointError(),
        PermissionMissingError.status_code: PermissionMissingError(),
    }
    api_exception = corresponding_api_exceptions.get(exception.status_code)

    if api_exception:
        return await on_api_exception(_, api_exception)
    else:
        return JSONResponse(
            status_code=exception.status_code,
            content=BaseResponse(status=exception.status_code).dict(
                exclude_none=True,
                exclude_unset=True,
                exclude_defaults=True,
            ),
        )


async def validation_exception_handler(_: Request, exc: ValidationError) -> JSONResponse:
    error_descriptions = [ValidationErrorDescription(**error) for error in exc.errors()]
    response_data = RequestParamValidationError().get_response_data()
    response_data.error.error_descriptions = error_descriptions  # type: ignore
    return JSONResponse(
        status_code=response_data.status,
        content=response_data.dict(exclude_none=True, exclude_unset=True, exclude_defaults=True),
    )


def include_exception_responses(*args: Type[BaseAPIException]) -> dict[Any, Any]:
    responses = {}
    for cls in args:
        responses.update(cls.response_model())
    return responses
