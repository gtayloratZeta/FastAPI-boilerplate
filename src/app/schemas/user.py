from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class UserBase(BaseModel):
    """
    Defines a data model for a user with validation rules. It has three attributes:
    `name`, `username`, and `email`, each with specific constraints on their values.

    Attributes:
        name (Annotated[str, Field(min_length=2, max_length=30, examples=["User
            Userson"])]): Restricted to strings of minimum length 2 and maximum
            length 30. It also includes examples of valid input, demonstrating how
            the attribute should be populated.
        username (Annotated[str, Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$",
            examples=["userson"])]): Represented as a string. It has a minimum
            length of 2 characters, a maximum length of 20 characters, and must
            match the regular expression pattern r"^[a-z0-9]+$", indicating that
            it can only contain lowercase letters and numbers.
        email (Annotated[EmailStr, Field(examples=["user.userson@example.com"])]):
            Defined to be a valid email address, with no specific length restrictions,
            but with the example of a valid email address provided.

    """
    name: Annotated[str, Field(min_length=2, max_length=30, examples=["User Userson"])]
    username: Annotated[str, Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", examples=["userson"])]
    email: Annotated[EmailStr, Field(examples=["user.userson@example.com"])]


class User(TimestampSchema, UserBase, UUIDSchema, PersistentDeletion):
    """
    Defines a user entity, inheriting from `TimestampSchema`, `UserBase`, `UUIDSchema`,
    and `PersistentDeletion`. It includes attributes for a default profile image
    URL, hashed password, superuser status, and tier ID, allowing for user account
    management.

    Attributes:
        profile_image_url (Annotated[str, Field(default="https://www.profileimageurl.com")]):
            Initialized with a default URL for a user's profile image, which is "https://www.profileimageurl.com".
        hashed_password (str): Used to store the hashed password of a user, implying
            it is encrypted for security purposes.
        is_superuser (bool): Initialized to False by default.
        tier_id (int | None): Optional, with a default value of None.

    """
    profile_image_url: Annotated[str, Field(default="https://www.profileimageurl.com")]
    hashed_password: str
    is_superuser: bool = False
    tier_id: int | None = None


class UserRead(BaseModel):
    """
    Defines a data model for reading user information, including id, name, username,
    email, profile image URL, and tier ID, with specified validation rules for
    name, username, and email fields.

    Attributes:
        id (int): Required, indicating that it must be present in any instance of
            the class.
        name (Annotated[str, Field(min_length=2, max_length=30, examples=["User
            Userson"])]): Defined as a string with a minimum length of 2 characters
            and a maximum length of 30 characters, and it includes example values
            such as "User Userson".
        username (Annotated[str, Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$",
            examples=["userson"])]): Validated to ensure it is a string with a
            minimum length of 2, maximum length of 20, and must consist only of
            lowercase letters and numbers.
        email (Annotated[EmailStr, Field(examples=["user.userson@example.com"])]):
            Validated as an email address.
        profile_image_url (str): Represented as a string, which can contain any
            valid URL for a profile image.
        tier_id (int | None): Represented as an integer that can optionally be
            None, indicating that it may not be present or may be empty.

    """
    id: int

    name: Annotated[str, Field(min_length=2, max_length=30, examples=["User Userson"])]
    username: Annotated[str, Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", examples=["userson"])]
    email: Annotated[EmailStr, Field(examples=["user.userson@example.com"])]
    profile_image_url: str
    tier_id: int | None


class UserCreate(UserBase):
    """
    Extends the `UserBase` class, inheriting its properties and methods. It defines
    a `model_config` attribute with additional configuration settings, specifically
    forbidding extra fields. The `password` attribute is annotated with a regular
    expression pattern for password validation.

    Attributes:
        model_config (ConfigDict): Configured with the extra argument set to "forbid".
        password (Annotated[str, Field(pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$",
            examples=["Str1ngst!"])]): Defined with a regular expression pattern
            that enforces a minimum length of 8 characters and checks for a
            combination of at least one uppercase letter, one lowercase letter,
            and one number, or a special character.

    """
    model_config = ConfigDict(extra="forbid")

    password: Annotated[str, Field(pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$", examples=["Str1ngst!"])]


class UserCreateInternal(UserBase):
    hashed_password: str


class UserUpdate(BaseModel):
    """
    Defines a data model for updating user information, validating fields such as
    name, username, email, and profile image URL through regular expressions and
    length constraints.

    Attributes:
        model_config (ConfigDict): Configured with the `extra` attribute set to
            `"forbid"`. This setting likely restricts or forbids additional
            attributes from being added to the model during runtime.
        name (Annotated[str | None, Field(min_length=2, max_length=30, examples=["User
            Userberg"], default=None)]): Defined with a minimum length of 2
            characters, a maximum length of 30 characters, and a default value of
            None.
        username (Annotated[
                    str | None, Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$",
            examples=["userberg"], default=None)
                ]): Validated by Pydantic to be a string with a minimum length of
            2, a maximum length of 20, and must match the regular expression pattern
            `^[a-z0-9]+$` which requires only lowercase letters and numbers.
        email (Annotated[EmailStr | None, Field(examples=["user.userberg@example.com"],
            default=None)]): Validated to be a valid email address, with a default
            value of None.
        profile_image_url (Annotated[
                    str | None,
                    Field(
                        pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$",
            examples=["https://www.profileimageurl.com"], default=None
                    ),
                ]): Validated to match a URL pattern. It must start with either
            'http://' or 'https://' or 'ftp://' and can contain any characters
            except whitespace, dollar sign, forward slash, question mark, period,
            and hash.

    """
    model_config = ConfigDict(extra="forbid")

    name: Annotated[str | None, Field(min_length=2, max_length=30, examples=["User Userberg"], default=None)]
    username: Annotated[
        str | None, Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", examples=["userberg"], default=None)
    ]
    email: Annotated[EmailStr | None, Field(examples=["user.userberg@example.com"], default=None)]
    profile_image_url: Annotated[
        str | None,
        Field(
            pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$", examples=["https://www.profileimageurl.com"], default=None
        ),
    ]


class UserUpdateInternal(UserUpdate):
    updated_at: datetime


class UserTierUpdate(BaseModel):
    tier_id: int


class UserDelete(BaseModel):
    """
    Represents a data model for user deletion status. It contains two attributes:
    `is_deleted` and `deleted_at`, indicating whether a user is deleted and when
    the deletion occurred, respectively.

    Attributes:
        model_config (ConfigDict): Configured to forbid extra attributes.
        is_deleted (bool): Representing a boolean flag indicating whether a user
            has been deleted.
        deleted_at (datetime): Representing the timestamp when the user was deleted.

    """
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime


class UserRestoreDeleted(BaseModel):
    is_deleted: bool
