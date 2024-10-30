import uuid as uuid_pkg
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class User(Base):
    """
    Defines a database table with attributes for user information, including id,
    name, username, email, password, profile image URL, and various timestamps for
    creation, updates, and deletion. It also includes foreign key references to a
    'tier' table.

    Attributes:
        __tablename__ (str): Used to specify the name of the database table that
            this class represents. In this case, the table name is "user".
        id (Mapped[int]): Mapped to a database column named "id" with the following
            characteristics: autoincrementing, not nullable, unique, and serving
            as the primary key.
        name (Mapped[str]): Mapped to a database column named `name` with a maximum
            length of 30 characters.
        username (Mapped[str]): Indexed uniquely, meaning it is used to create a
            unique index on the `username` column in the database.
        email (Mapped[str]): Mapped to a database column with the following characteristics:
            String length of 50 characters, unique, and indexed.
        hashed_password (Mapped[str]): Mapped to a database column of type String.
            It is used to store hashed passwords for user authentication purposes.
        profile_image_url (Mapped[str]): Mapped to a database column with a default
            value of "https://profileimageurl.com", indicating a default URL for
            user profile images.
        uuid (Mapped[uuid_pkg.UUID]): Defined with a default factory using
            `uuid_pkg.uuid4`, which generates a unique identifier. It is also a
            primary key and unique.
        created_at (Mapped[datetime]): Mapped to a column in the database with the
            data type DateTime. The timezone is set to True, indicating that the
            data is stored in a timezone-aware format. By default, it is automatically
            set to the current time in UTC whenever a new user is created.
        updated_at (Mapped[datetime | None]): Mapped to a database column with a
            data type of DateTime and timezone support. It defaults to None,
            indicating the time when the user's record was last updated.
        deleted_at (Mapped[datetime | None]): Mapped to a column in the database
            with the name "deleted_at". It is nullable, and its default value is
            None. This suggests that the attribute tracks when a user record is deleted.
        is_deleted (Mapped[bool]): Indexed. It is initially set to False and is
            not nullable.
        is_superuser (Mapped[bool]): Defined with a default value of `False`. It
            is also indexed, indicating that it may be used in database queries
            for efficient retrieval of data.
        tier_id (Mapped[int | None]): Mapped to a foreign key referencing the "id"
            column of the "tier" table. It is nullable, indexed, and has a default
            value of None.

    """
    __tablename__ = "user"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)

    name: Mapped[str] = mapped_column(String(30))
    username: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)

    profile_image_url: Mapped[str] = mapped_column(String, default="https://profileimageurl.com")
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(default_factory=uuid_pkg.uuid4, primary_key=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    tier_id: Mapped[int | None] = mapped_column(ForeignKey("tier.id"), index=True, default=None, init=False)
