import uuid as uuid_pkg
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, field_serializer


class HealthCheck(BaseModel):
    """
    Defines a data model for health checks, including a name, version, and
    description. It is likely used to represent health check information in a
    structured and consistent manner, possibly for API responses or database storage.

    Attributes:
        name (str): Required, indicating that it must be specified when creating
            an instance of the `HealthCheck` class.
        version (str): A string representing the version of the health check.
        description (str): A required field, implying it must be provided when
            creating an instance of the `HealthCheck` class.

    """
    name: str
    version: str
    description: str


# -------------- mixins --------------
class UUIDSchema(BaseModel):
    uuid: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4)


class TimestampSchema(BaseModel):
    """
    Defines a data model for timestamps. It includes two fields: `created_at` and
    `updated_at`. The `created_at` field automatically sets the current date and
    time when an instance is created, while the `updated_at` field remains unset
    unless explicitly set.

    Attributes:
        created_at (datetime): Initialized with the current date and time in UTC
            when an instance of the class is created.
        updated_at (datetime): Initialized with a default value of None.

    """
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at: datetime = Field(default=None)

    @field_serializer("created_at")
    def serialize_dt(self, created_at: datetime | None, _info: Any) -> str | None:
        """
        Converts a datetime object to a string in ISO format if it is not None,
        otherwise returns None.

        Args:
            created_at (datetime | None): Representing the date and time when an
                object was created. It may be None if the creation time is unknown.
            _info (Any): Used internally by the `field_serializer` decorator,
                likely to store metadata or additional context about the serialization
                process.

        Returns:
            str | None: Either a string representation of a datetime object in ISO
            format or None if the input datetime object is None.

        """
        if created_at is not None:
            return created_at.isoformat()

        return None

    @field_serializer("updated_at")
    def serialize_updated_at(self, updated_at: datetime | None, _info: Any) -> str | None:
        """
        Serializes a datetime object to ISO format if it exists, otherwise returns
        None.

        Args:
            updated_at (datetime | None): Representing a date and time value,
                possibly null.
            _info (Any): Passed to the function to provide additional information,
                which is not used in this specific function implementation.

        Returns:
            str | None: Either the ISO-formatted string representation of the
            `updated_at` datetime object, or None if `updated_at` is None.

        """
        if updated_at is not None:
            return updated_at.isoformat()

        return None


class PersistentDeletion(BaseModel):
    """
    Tracks the deletion status of an object. It contains `deleted_at` and `is_deleted`
    fields, where `deleted_at` stores the timestamp of deletion and `is_deleted`
    indicates whether the object has been deleted.

    Attributes:
        deleted_at (datetime | None): Initialized with a default value of None.
            It represents a timestamp when the object is deleted.
        is_deleted (bool): Initialized to False.

    """
    deleted_at: datetime | None = Field(default=None)
    is_deleted: bool = False

    @field_serializer("deleted_at")
    def serialize_dates(self, deleted_at: datetime | None, _info: Any) -> str | None:
        """
        Serializes a datetime object representing the 'deleted_at' date into ISO
        format, returning it as a string if 'deleted_at' is not None, otherwise
        returning None.

        Args:
            deleted_at (datetime | None): Representing a date and time when an
                item was deleted, potentially being None if it has not been deleted.
            _info (Any): Used internally by the field serializer and is not used
                in the provided function.

        Returns:
            str | None: The ISO-formatted string representation of the datetime
            object if it exists, otherwise None.

        """
        if deleted_at is not None:
            return deleted_at.isoformat()

        return None


# -------------- token --------------
class Token(BaseModel):
    """
    Represents a token model with two fields: `access_token` and `token_type`,
    both of type `str`. This class is likely used to store and validate tokens
    obtained from authentication services.

    Attributes:
        access_token (str): A string representing the access token, likely used
            for authentication and authorization purposes.
        token_type (str): Described as a string indicating the type of token, such
            as Bearer or other token types used in authentication protocols.

    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username_or_email: str


class TokenBlacklistBase(BaseModel):
    """
    Defines a data model for token blacklisting, storing a token and its expiration
    time in a structured format.

    Attributes:
        token (str): Representing a string that contains a token, likely a unique
            identifier.
        expires_at (datetime): Used to store a specific date and time when a token
            will expire. It is likely used in conjunction with the `token` attribute
            to manage the blacklist of tokens.

    """
    token: str
    expires_at: datetime


class TokenBlacklistCreate(TokenBlacklistBase):
    pass


class TokenBlacklistUpdate(TokenBlacklistBase):
    pass
