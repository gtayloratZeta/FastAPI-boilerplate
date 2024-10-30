from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from ..core.schemas import PersistentDeletion, TimestampSchema, UUIDSchema


class PostBase(BaseModel):
    """
    Defines a data model for posts with two attributes: `title` and `text`. The
    `title` must be between 2 and 30 characters long, while the `text` can be up
    to 63,206 characters long. Both fields have example values provided.

    Attributes:
        title (Annotated[str, Field(min_length=2, max_length=30, examples=["This
            is my post"])]): Defined as a string with a minimum length of 2
            characters and a maximum length of 30 characters.
        text (Annotated[str, Field(min_length=1, max_length=63206, examples=["This
            is the content of my post."])]): Defined as a string with a minimum
            length of 1 and a maximum length of 63206 characters.

    """
    title: Annotated[str, Field(min_length=2, max_length=30, examples=["This is my post"])]
    text: Annotated[str, Field(min_length=1, max_length=63206, examples=["This is the content of my post."])]


class Post(TimestampSchema, PostBase, UUIDSchema, PersistentDeletion):
    """
    Defines a data model for a post with attributes for media URL, creation by a
    user, and timestamp information, inheriting from base classes for timestamp,
    post base, UUID, and persistent deletion.

    Attributes:
        media_url (Annotated[
                    str | None,
                    Field(pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$",
            examples=["https://www.postimageurl.com"], default=None),
                ]): Used to store a URL of a media, which can be either a string
            or None. The URL is validated to match a specific pattern, ensuring
            it is a valid HTTP or FTP URL.
        created_by_user_id (int): Related to a user who created the post. It
            represents the user's identifier.

    """
    media_url: Annotated[
        str | None,
        Field(pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$", examples=["https://www.postimageurl.com"], default=None),
    ]
    created_by_user_id: int


class PostRead(BaseModel):
    """
    Defines a data model for reading posts, which includes attributes for post
    identification, title, content, associated media URL, creator's user ID, and
    creation timestamp.

    Attributes:
        id (int): A unique identifier for a post, likely serving as a primary key
            in a database.
        title (Annotated[str, Field(min_length=2, max_length=30, examples=["This
            is my post"])]): Required to be a string with a minimum length of 2
            and a maximum length of 30 characters.
        text (Annotated[str, Field(min_length=1, max_length=63206, examples=["This
            is the content of my post."])]): Defined with a minimum length of 1
            character and a maximum length of 63206 characters.
        media_url (Annotated[
                    str | None,
                    Field(examples=["https://www.postimageurl.com"], default=None),
                ]): Optional, allowing it to be either a valid URL string or None.
        created_by_user_id (int): Represented by a unique identifier of the user
            who created the post.
        created_at (datetime): Defined as a field in the class, implying that it
            represents the time at which a post was created.

    """
    id: int
    title: Annotated[str, Field(min_length=2, max_length=30, examples=["This is my post"])]
    text: Annotated[str, Field(min_length=1, max_length=63206, examples=["This is the content of my post."])]
    media_url: Annotated[
        str | None,
        Field(examples=["https://www.postimageurl.com"], default=None),
    ]
    created_by_user_id: int
    created_at: datetime


class PostCreate(PostBase):
    """
    Derives from the `PostBase` class and extends its functionality, specifically
    configuring a model using a `ConfigDict` instance. It also defines a `media_url`
    field, which is a string that can be either a valid URL or `None`, with a
    specified pattern and default value.

    Attributes:
        model_config (ConfigDict): Configured with the extra parameter set to
            "forbid", indicating that it does not accept any additional configuration.
        media_url (Annotated[
                    str | None,
                    Field(pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$",
            examples=["https://www.postimageurl.com"], default=None),
                ]): Defined as a string or None type, with a regular expression
            pattern to validate URLs, and examples of valid URLs, including a
            default value of None.

    """
    model_config = ConfigDict(extra="forbid")

    media_url: Annotated[
        str | None,
        Field(pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$", examples=["https://www.postimageurl.com"], default=None),
    ]


class PostCreateInternal(PostCreate):
    created_by_user_id: int


class PostUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Annotated[str | None, Field(min_length=2, max_length=30, examples=["This is my updated post"], default=None)]
    text: Annotated[
        str | None,
        Field(min_length=1, max_length=63206, examples=["This is the updated content of my post."], default=None),
    ]
    media_url: Annotated[
        str | None,
        Field(pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$", examples=["https://www.postimageurl.com"], default=None),
    ]


class PostUpdateInternal(PostUpdate):
    updated_at: datetime


class PostDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_deleted: bool
    deleted_at: datetime
