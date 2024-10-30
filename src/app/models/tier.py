from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class Tier(Base):
    """
    Defines a database table named "tier" with four columns: id, name, created_at,
    and updated_at. The id is an auto-incrementing primary key, and the name is a
    unique string. The created_at column stores the current date and time in UTC,
    while the updated_at column stores the last update time or null.

    Attributes:
        __tablename__ (str): Used to specify the name of the database table
            associated with the class.
        id (Mapped[int]): Mapped to a column named "id" in the "tier" table. It
            has several properties: autoincrement, not nullable, unique, and serves
            as the primary key.
        name (Mapped[str]): Mapped to a column named "name" in the "tier" table.
            It is a required field, meaning it cannot be null, and its values must
            be unique.
        created_at (Mapped[datetime]): Automatically set to the current UTC time
            when a new instance of the `Tier` class is created, thanks to the
            `default_factory` parameter of the `mapped_column` function.
        updated_at (Mapped[datetime | None]): Mapped to a database column with the
            type DateTime(timezone=True). The default value is None.

    """
    __tablename__ = "tier"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
