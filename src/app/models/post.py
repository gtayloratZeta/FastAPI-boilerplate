import uuid as uuid_pkg
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class Post(Base):
    """
    Represents a database table for posts, mapping columns to attributes with
    attributes such as auto-incrementing IDs, foreign keys, timestamps, and deletion
    flags, facilitating data storage and retrieval in a database system.

    Attributes:
        __tablename__ (str): Used to specify the name of the database table
            associated with the `Post` class. In this case, it is set to `"post"`.
        id (Mapped[int]): Mapped to a column named "id" in the database table
            "post". It is an autoincrementing primary key, meaning it will be
            automatically assigned a unique integer value when a new post is
            created, and it cannot be null.
        created_by_user_id (Mapped[int]): Mapped to a column in the "post" table.
            It references the "id" column of the "user" table through a foreign
            key relationship. This establishes a connection between a post and its
            creator.
        title (Mapped[str]): Mapped to a database column named "title" with a
            maximum length of 30 characters.
        text (Mapped[str]): Mapped to a database column of type String with a
            maximum length of 63206 characters.
        uuid (Mapped[uuid_pkg.UUID]): Assigned a unique identifier using the
            `default_factory` parameter of the `mapped_column` function, which
            generates a random UUID using the `uuid4` function from the `uuid_pkg`
            package.
        media_url (Mapped[str | None]): Indexed and has a default value of None.
        created_at (Mapped[datetime]): Backed by a database column of type DateTime
            with timezone support. It defaults to the current date and time in UTC
            when a new post is created.
        updated_at (Mapped[datetime | None]): Mapped to a database column with the
            same name. It defaults to None and is mapped to a DateTime column with
            timezone support, allowing for possible updates to the post.
        deleted_at (Mapped[datetime | None]): Mapped to a database column with the
            name "deleted_at". It represents the date and time when a post is
            deleted. The attribute has a default value of None.
        is_deleted (Mapped[bool]): Indexed. It defaults to False and can be
            optionally set to indicate a post's deletion status.

    """
    __tablename__ = "post"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    title: Mapped[str] = mapped_column(String(30))
    text: Mapped[str] = mapped_column(String(63206))
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(default_factory=uuid_pkg.uuid4, primary_key=True, unique=True)
    media_url: Mapped[str | None] = mapped_column(String, default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
