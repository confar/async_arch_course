from typing import Any, Optional, Union

from fastapi import status as status_code
from pydantic import BaseModel, Field


class BaseError(BaseModel):
    """Error response as defined in
    https://datatracker.ietf.org/doc/html/rfc7807.

    One difference is that the member "type" is not a URI
    """

    type: Optional[str] = Field(title="The name of the class of the error")
    title: Optional[str] = Field(
        title="A short, human-readable summary of the problem that does not change from occurence to occurence",
    )
    detail: Optional[str] = Field(title="А human-readable explanation specific to this occurrence of the problem")
    instance: Optional[Any] = Field(title="Identifier for this specific occurrence of the problem")


class BaseResponse(BaseModel):
    status: int = Field(..., title="Status code of request.", example=status_code.HTTP_200_OK)
    error: Union[dict[Any, Any], BaseError] = Field({}, title="Errors")
    payload: Optional[Any] = Field({}, title="Payload data.")


class NoContentResponse(BaseResponse):
    status: int = status_code.HTTP_204_NO_CONTENT
