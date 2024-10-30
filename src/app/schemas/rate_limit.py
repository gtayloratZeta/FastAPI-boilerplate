from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..core.schemas import TimestampSchema


def sanitize_path(path: str) -> str:
    return path.strip("/").replace("/", "_")


class RateLimitBase(BaseModel):
    """
    Defines a base model for rate limiting, consisting of `path`, `limit`, and
    `period` fields. It includes a field validator that sanitizes the `path` field
    using the `sanitize_path` function, ensuring it is valid and properly formatted.

    Attributes:
        path (Annotated[str, Field(examples=["users"])]): Defined as a string that
            represents a path, with a default example value of "users".
        limit (Annotated[int, Field(examples=[5])]): Represented by an integer
            value, which is the maximum number of requests allowed within a specified
            time period.
        period (Annotated[int, Field(examples=[60])]): Represented by an integer
            value indicating the time period in seconds during which a certain
            number of requests are allowed.

    """
    path: Annotated[str, Field(examples=["users"])]
    limit: Annotated[int, Field(examples=[5])]
    period: Annotated[int, Field(examples=[60])]

    @field_validator("path")
    def validate_and_sanitize_path(cls, v: str) -> str:
        """
        Validates and sanitizes a given path. It calls another function,
        `sanitize_path`, to perform the actual validation and sanitization.

        Args:
            v (str): A positional-only parameter, which means it must be passed
                positionally and cannot be used as a keyword argument.

        Returns:
            str: The sanitized version of the input string, following a call to
            the `sanitize_path` function.

        """
        return sanitize_path(v)


class RateLimit(TimestampSchema, RateLimitBase):
    """
    Extends `TimestampSchema` and `RateLimitBase`, inheriting their functionality.
    It defines two attributes: `tier_id` of type `int` and `name` of type `str |
    None`, which can be annotated with examples.

    Attributes:
        tier_id (int): Inherited from the `RateLimitBase` class.
        name (Annotated[str | None, Field(default=None, examples=["users:5:60"])]):
            Annotated with a default value of None and examples of valid values,
            including "users:5:60".

    """
    tier_id: int
    name: Annotated[str | None, Field(default=None, examples=["users:5:60"])]


class RateLimitRead(RateLimitBase):
    """
    Extends the `RateLimitBase` class, defining a specific rate limit configuration
    for read operations. It appears to be a data model for a rate limit tier,
    containing attributes such as `id`, `tier_id`, and `name`.

    Attributes:
        id (int): Used to uniquely identify a rate limit read object.
        tier_id (int): Associated with a tier.
        name (str): Designated to hold a string representing the name of the rate
            limit read.

    """
    id: int
    tier_id: int
    name: str


class RateLimitCreate(RateLimitBase):
    """
    Extends the `RateLimitBase` class and defines configuration settings for rate
    limiting. It specifies a model configuration as a dictionary with an extra
    key, and a name field that can be a string or None, defaulting to None.

    Attributes:
        model_config (Dict[str,str]): Configured with a default value of `ConfigDict(extra="forbid")`.
        name (Annotated[str | None, Field(default=None, examples=["api_v1_users:5:60"])]):
            Defined as a string or None type. It has a default value of None and
            examples of valid input, such as "api_v1_users:5:60".

    """
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str | None, Field(default=None, examples=["api_v1_users:5:60"])]


class RateLimitCreateInternal(RateLimitCreate):
    tier_id: int


class RateLimitUpdate(BaseModel):
    """
    Models an update to a rate limit, containing path, limit, period, and name
    fields, with a validator function to sanitize and validate the path.

    Attributes:
        path (str | None): Optional. It represents a path and can be None. It has
            a custom validation and sanitization process when not None.
        limit (int | None): Initialized with a default value of None.
        period (int | None): Defined to store an integer value representing the
            time period, presumably in seconds, over which the rate limit applies.
        name (str | None): Optional. It is used to store a name, but its purpose
            and usage are not specified in the provided code.

    """
    path: str | None = Field(default=None)
    limit: int | None = None
    period: int | None = None
    name: str | None = None

    @field_validator("path")
    def validate_and_sanitize_path(cls, v: str) -> str:
        """
        Validates and sanitizes a path string. If the input is not None, it calls
        the sanitize_path function with the input and returns the result. Otherwise,
        it returns None.

        Args:
            v (str): Assigned the value of the validated field, specifically the
                "path" field.

        Returns:
            str: The sanitized path if the input path is not None, otherwise it
            returns None.

        """
        return sanitize_path(v) if v is not None else None


class RateLimitUpdateInternal(RateLimitUpdate):
    updated_at: datetime


class RateLimitDelete(BaseModel):
    pass
