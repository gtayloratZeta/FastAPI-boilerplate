import uuid as uuid_pkg
from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, text
from sqlalchemy.dialects.postgresql import UUID


class UUIDMixin:
    """
    Defines a mixin class that automatically generates a unique identifier for
    database records using the UUID (Universally Unique Identifier) standard. It
    uses the `uuid4` function to generate a random UUID and the `gen_random_uuid()`
    function to generate a UUID based on the PostgreSQL server's random number generator.

    Attributes:
        uuid (uuid_pkg.UUID): Defined as a Column in a database table. It has
            several properties:
            - Type: UUID
            - Primary key: True
            - Default value: uuid_pkg.uuid4
            - Server default value: gen_random_uuid()

    """
    uuid: uuid_pkg.UUID = Column(
        UUID, primary_key=True, default=uuid_pkg.uuid4, server_default=text("gen_random_uuid()")
    )


class TimestampMixin:
    """
    Automatically tracks the creation and last update timestamps of database
    records. The `created_at` field is set upon record creation, while the
    `updated_at` field is updated upon each update, assuming a timestamp-based database.

    Attributes:
        created_at (datetime): Defined as a database column with the name `created_at`.
            It represents the time when a record is created. It defaults to the
            current time in UTC when a new record is inserted into the database.
        updated_at (datetime): Used to track the last time the associated database
            record was updated. It defaults to the current timestamp when a new
            record is created, and is automatically updated to the current timestamp
            whenever the record is updated.

    """
    created_at: datetime = Column(DateTime, default=datetime.now(UTC), server_default=text("current_timestamp(0)"))
    updated_at: datetime = Column(
        DateTime, nullable=True, onupdate=datetime.now(UTC), server_default=text("current_timestamp(0)")
    )


class SoftDeleteMixin:
    """
    Implements a mixin for soft deletion functionality, providing two columns:
    `deleted_at` to track the deletion time and `is_deleted` to indicate whether
    the record has been deleted, with a default value of False.

    Attributes:
        deleted_at (datetime): Nullable, indicating that a row may or may not have
            a value for the deletion timestamp.
        is_deleted (bool): Defined as a column in the database table. It has a
            default value of False, indicating that the record is not deleted.

    """
    deleted_at: datetime = Column(DateTime, nullable=True)
    is_deleted: bool = Column(Boolean, default=False)
