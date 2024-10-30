from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class TokenBlacklist(Base):
    """
    Defines a database table to store blacklisted tokens for security purposes.
    It has three columns: `id` for unique identification, `token` for storing the
    blacklisted token, and `expires_at` for tracking when the token expires.

    Attributes:
        __tablename__ (Any): Used to specify the name of the database table
            associated with the class.
        id (Mapped[int]): Mapped to a database column named "id". It is an
            auto-incrementing primary key, ensuring uniqueness and non-nullability.
        token (Mapped[str]): Mapped to a column named "token" in the database
            table. It is defined to be unique and indexed.
        expires_at (Mapped[datetime]): Mapped to a database column named "expires_at".

    """
    __tablename__ = "token_blacklist"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    token: Mapped[str] = mapped_column(String, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
