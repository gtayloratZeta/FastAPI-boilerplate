from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class RateLimit(Base):
    """
    Defines a database table for rate limiting rules, with attributes for tier ID,
    name, path, limit, period, creation and update timestamps, and a primary key.

    Attributes:
        __tablename__ (str): Set to the string "rate_limit", specifying the name
            of the database table that this class will map to.
        id (Mapped[int]): Mapped to a database column named "id". It is an
            auto-incrementing primary key, meaning it automatically assigns a
            unique integer value to each record, and it cannot be null.
        tier_id (Mapped[int]): Mapped to a foreign key referencing the "tier.id"
            column in the "tier" table.
        name (Mapped[str]): Mapped to a column named `name` in the "rate_limit"
            table. It is nullable, meaning it can be null, and unique, meaning no
            two rows in the table can have the same value for this column.
        path (Mapped[str]): Mapped to a database column with the type String and
            is nullable.
        limit (Mapped[int]): Mapped to a database column named "limit" of type
            Integer, indicating the maximum number of requests allowed within a
            given time period.
        period (Mapped[int]): Mapped to a database column of type Integer. It
            represents the time period in seconds.
        created_at (Mapped[datetime]): Tracked in the "rate_limit" table with a
            column named "created_at". This column is of type DateTime with timezone
            support and defaults to the current UTC time when a new instance of
            `RateLimit` is created.
        updated_at (Mapped[datetime | None]): Defined with a `DateTime` mapped
            column. It has a default value of `None` and does not use a default
            factory function.

    """
    __tablename__ = "rate_limit"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    tier_id: Mapped[int] = mapped_column(ForeignKey("tier.id"), index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    path: Mapped[str] = mapped_column(String, nullable=False)
    limit: Mapped[int] = mapped_column(Integer, nullable=False)
    period: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
