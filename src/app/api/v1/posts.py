from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_superuser, get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import ForbiddenException, NotFoundException
from ...core.utils.cache import cache
from ...crud.crud_posts import crud_posts
from ...crud.crud_users import crud_users
from ...schemas.post import PostCreate, PostCreateInternal, PostRead, PostUpdate
from ...schemas.user import UserRead

router = APIRouter(tags=["posts"])


@router.post("/{username}/post", response_model=PostRead, status_code=201)
async def write_post(
    request: Request,
    username: str,
    post: PostCreate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> PostRead:
    """
    Allows a user to create a new post. It validates the user's identity, checks
    for the existence of the specified user, and then creates a new post in the
    database with the user's ID as the creator.

    Args:
        request (Request): Required for the function to access the HTTP request.
        username (str): Derived from the path parameter of the route, specified
            by the `@router.post("/{username}/post"` decorator.
        post (PostCreate): Bound to a POST request body. It represents the data
            for the new post being created.
        current_user (Annotated[UserRead, Depends(get_current_user)]): Injected
            by the `get_current_user` dependency, which likely returns the currently
            authenticated user's data.
        db (Annotated[AsyncSession, Depends(async_get_db)]): A database session
            object used for asynchronous database operations. It is obtained from
            the `async_get_db` dependency.

    Returns:
        PostRead: An instance of the PostRead model, representing a newly created
        post.

    """
    db_user = await crud_users.get(db=db, schema_to_select=UserRead, username=username, is_deleted=False)
    if db_user is None:
        raise NotFoundException("User not found")

    if current_user["id"] != db_user["id"]:
        raise ForbiddenException()

    post_internal_dict = post.model_dump()
    post_internal_dict["created_by_user_id"] = db_user["id"]

    post_internal = PostCreateInternal(**post_internal_dict)
    created_post: PostRead = await crud_posts.create(db=db, object=post_internal)
    return created_post


@router.get("/{username}/posts", response_model=PaginatedListResponse[PostRead])
@cache(
    key_prefix="{username}_posts:page_{page}:items_per_page:{items_per_page}",
    resource_id_name="username",
    expiration=60,
)
async def read_posts(
    request: Request,
    username: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = 1,
    items_per_page: int = 10,
) -> dict:
    """
    Retrieves a paginated list of posts created by a specified user from the
    database. It first checks if the user exists, and if not, it raises a "User
    not found" exception.

    Args:
        request (Request): Used to access the current HTTP request.
        username (str): Extracted from the path parameter of the route, specified
            by the path parameter `"{username}"` in the `@router.get` decorator.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Injected by the
            `async_get_db` dependency. It represents an asynchronous database session.
        page (int): Optional. It defaults to 1 if not provided.
        items_per_page (int): Defaulted to 10, specifying the number of items to
            be displayed on each page of the paginated response.

    Returns:
        dict: A paginated list of posts in JSON format, containing the posts data,
        total count, page number, and items per page.

    """
    db_user = await crud_users.get(db=db, schema_to_select=UserRead, username=username, is_deleted=False)
    if not db_user:
        raise NotFoundException("User not found")

    posts_data = await crud_posts.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=PostRead,
        created_by_user_id=db_user["id"],
        is_deleted=False,
    )

    response: dict[str, Any] = paginated_response(crud_data=posts_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/{username}/post/{id}", response_model=PostRead)
@cache(key_prefix="{username}_post_cache", resource_id_name="id")
async def read_post(
    request: Request, username: str, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict:
    """
    Retrieves a post by its ID from the database for a given username, ensuring
    the user and post exist and are not deleted. It returns the post data in the
    PostRead schema, or raises a NotFoundException if either the user or post is
    not found.

    Args:
        request (Request): Required for the function to receive the HTTP request
            from the client.
        username (str): Extracted from the path of the HTTP request, specifically
            from the "/{username}/post/{id}" path.
        id (int): Extracted from the path of the route as `{id}` and used to
            identify a specific post in the database. It is also used as a key in
            the cache with the `key_prefix` set to the username and the
            `resource_id_name` set to `id`.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Injected into the
            function through the `Depends` dependency. It represents an asynchronous
            database session that is retrieved by the `async_get_db` function.

    Returns:
        dict: A representation of a `PostRead` object.

    """
    db_user = await crud_users.get(db=db, schema_to_select=UserRead, username=username, is_deleted=False)
    if db_user is None:
        raise NotFoundException("User not found")

    db_post: PostRead | None = await crud_posts.get(
        db=db, schema_to_select=PostRead, id=id, created_by_user_id=db_user["id"], is_deleted=False
    )
    if db_post is None:
        raise NotFoundException("Post not found")

    return db_post


@router.patch("/{username}/post/{id}")
@cache("{username}_post_cache", resource_id_name="id", pattern_to_invalidate_extra=["{username}_posts:*"])
async def patch_post(
    request: Request,
    username: str,
    id: int,
    values: PostUpdate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    """
    Updates a post with the specified ID for the given username. It checks for
    user and post existence, ensures the current user is the owner, and returns a
    success message upon a successful update.

    Args:
        request (Request): A representation of the HTTP request made to the endpoint.
        username (str): Extracted from the path of the incoming request, specifically
            from the URL path "/{username}/post/{id}".
        id (int): A path parameter that represents the ID of a post, as specified
            by the `@router.patch("/{username}/post/{id}"` decorator.
        values (PostUpdate): Bound to an instance of the PostUpdate class, which
            is likely a Pydantic model representing the data to be updated in the
            post.
        current_user (Annotated[UserRead, Depends(get_current_user)]): Injected
            by the `get_current_user` dependency. It represents the currently
            authenticated user.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Injected by the
            `async_get_db` dependency. It represents a database session for
            asynchronous database operations.

    Returns:
        dict[str, str]: A dictionary containing a single key-value pair where the
        key is "message" and the value is the string "Post updated".

    """
    db_user = await crud_users.get(db=db, schema_to_select=UserRead, username=username, is_deleted=False)
    if db_user is None:
        raise NotFoundException("User not found")

    if current_user["id"] != db_user["id"]:
        raise ForbiddenException()

    db_post = await crud_posts.get(db=db, schema_to_select=PostRead, id=id, is_deleted=False)
    if db_post is None:
        raise NotFoundException("Post not found")

    await crud_posts.update(db=db, object=values, id=id)
    return {"message": "Post updated"}


@router.delete("/{username}/post/{id}")
@cache("{username}_post_cache", resource_id_name="id", to_invalidate_extra={"{username}_posts": "{username}"})
async def erase_post(
    request: Request,
    username: str,
    id: int,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    """
    Handles a DELETE request to delete a post by a specific user. It checks if the
    user exists, if the user has the necessary permissions, and if the post exists
    before deleting it from the database.

    Args:
        request (Request): A dependency injected by the framework, representing
            the incoming HTTP request.
        username (str): Extracted from the path of the HTTP request. It is a path
            parameter, specified in the route definition `@router.delete("/{username}/post/{id}"`.
        id (int): Bound to the value of a path parameter in the route, which is
            the ID of a post to be deleted. It is used to identify the post uniquely.
        current_user (Annotated[UserRead, Depends(get_current_user)]): Dependent
            on a dependency named `get_current_user`. This implies that
            `get_current_user` is a dependency that retrieves the current user.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Injected by the
            `async_get_db` dependency, providing a database session to perform
            CRUD operations.

    Returns:
        dict[str, str]: A dictionary containing a single key-value pair with the
        key "message" and the value "Post deleted".

    """
    db_user = await crud_users.get(db=db, schema_to_select=UserRead, username=username, is_deleted=False)
    if db_user is None:
        raise NotFoundException("User not found")

    if current_user["id"] != db_user["id"]:
        raise ForbiddenException()

    db_post = await crud_posts.get(db=db, schema_to_select=PostRead, id=id, is_deleted=False)
    if db_post is None:
        raise NotFoundException("Post not found")

    await crud_posts.delete(db=db, id=id)

    return {"message": "Post deleted"}


@router.delete("/{username}/db_post/{id}", dependencies=[Depends(get_current_superuser)])
@cache("{username}_post_cache", resource_id_name="id", to_invalidate_extra={"{username}_posts": "{username}"})
async def erase_db_post(
    request: Request, username: str, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    """
    Permanently deletes a post from the database for a given user and returns a
    success message upon successful deletion.

    Args:
        request (Request): Typically an instance of a request object that represents
            the HTTP request being processed.
        username (str): Extracted from the path of the URL. It corresponds to the
            username in the URL path `/username/db_post/{id}`.
        id (int): Bound to the path parameter `{id}` in the route, indicating it
            is a required path parameter in the URL.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Injected via dependency
            injection, using a dependency named `async_get_db`, which returns an
            instance of `AsyncSession`, a database session.

    Returns:
        dict[str, str]: A dictionary containing a single key-value pair, where the
        key is "message" and the value is the string "Post deleted from the database".

    """
    db_user = await crud_users.get(db=db, schema_to_select=UserRead, username=username, is_deleted=False)
    if db_user is None:
        raise NotFoundException("User not found")

    db_post = await crud_posts.get(db=db, schema_to_select=PostRead, id=id, is_deleted=False)
    if db_post is None:
        raise NotFoundException("Post not found")

    await crud_posts.db_delete(db=db, id=id)
    return {"message": "Post deleted from the database"}
