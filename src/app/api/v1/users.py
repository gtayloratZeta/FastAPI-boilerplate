from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_superuser, get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, ForbiddenException, NotFoundException
from ...core.security import blacklist_token, get_password_hash, oauth2_scheme
from ...crud.crud_rate_limit import crud_rate_limits
from ...crud.crud_tier import crud_tiers
from ...crud.crud_users import crud_users
from ...models.tier import Tier
from ...schemas.tier import TierRead
from ...schemas.user import UserCreate, UserCreateInternal, UserRead, UserTierUpdate, UserUpdate

router = APIRouter(tags=["users"])


@router.post("/user", response_model=UserRead, status_code=201)
async def write_user(
    request: Request, user: UserCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> UserRead:
    """
    Creates a new user in the database. It checks for existing email and username,
    hashes the password, and returns the newly created user's details with a 201
    status code.

    Args:
        request (Request): Used to represent the incoming HTTP request. It is
            likely a Pydantic model that encapsulates information about the request.
        user (UserCreate): Required for the function to run properly. It represents
            the user data being created. The `UserCreate` type likely contains the
            attributes for a new user, such as email and username.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Injected by the
            `Depends` decorator from the `async_get_db` function, which likely
            returns an instance of `AsyncSession` representing a database session.

    Returns:
        UserRead: A representation of a user in a readable format.

    """
    email_row = await crud_users.exists(db=db, email=user.email)
    if email_row:
        raise DuplicateValueException("Email is already registered")

    username_row = await crud_users.exists(db=db, username=user.username)
    if username_row:
        raise DuplicateValueException("Username not available")

    user_internal_dict = user.model_dump()
    user_internal_dict["hashed_password"] = get_password_hash(password=user_internal_dict["password"])
    del user_internal_dict["password"]

    user_internal = UserCreateInternal(**user_internal_dict)
    created_user: UserRead = await crud_users.create(db=db, object=user_internal)
    return created_user


@router.get("/users", response_model=PaginatedListResponse[UserRead])
async def read_users(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10
) -> dict:
    """
    Handles a GET request to retrieve a paginated list of users. It fetches data
    from the database, applies pagination, and returns a dictionary containing the
    paginated list of users.

    Args:
        request (Request): Required for the function to operate, as it is used to
            obtain the current request.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Injected through
            dependency injection using the `async_get_db` function. This function
            likely returns an asynchronous database session.
        page (int): Optional, with a default value of 1. It specifies the page
            number of users to retrieve.
        items_per_page (int): Optional, defaulting to 10. It specifies the number
            of users to return per page of the paginated response.

    Returns:
        dict: A paginated response containing a list of users, along with metadata
        such as the current page number and the total number of pages.

    """
    users_data = await crud_users.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=UserRead,
        is_deleted=False,
    )

    response: dict[str, Any] = paginated_response(crud_data=users_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/user/me/", response_model=UserRead)
async def read_users_me(request: Request, current_user: Annotated[UserRead, Depends(get_current_user)]) -> UserRead:
    """
    Handles HTTP GET requests to the "/user/me/" endpoint. It retrieves and returns
    the currently authenticated user's data, utilizing the `get_current_user`
    dependency to validate user authentication.

    Args:
        request (Request): A parameter that represents the HTTP request received
            by the function.
        current_user (Annotated[UserRead, Depends(get_current_user)]): Resolved
            through the `Depends` function, which calls the `get_current_user`
            function to obtain the current user.

    Returns:
        UserRead: An annotated object that represents a user's data in a readable
        format.

    """
    return current_user


@router.get("/user/{username}", response_model=UserRead)
async def read_user(request: Request, username: str, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict:
    """
    Retrieves a user from the database based on a provided username, validates
    that the user exists and is not deleted, and returns the user data in the
    `UserRead` format.

    Args:
        request (Request): A part of the FastAPI request object. It likely contains
            information about the incoming HTTP request.
        username (str): Defined by the path operation decorator
            `@router.get("/user/{username}")`, indicating it is extracted from the
            URL path.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Injected by the
            `async_get_db` dependency using the `Depends` decorator, which returns
            an instance of `AsyncSession` from the database.

    Returns:
        dict: An instance of the `UserRead` class, containing information about
        the user with the specified `username`.

    """
    db_user: UserRead | None = await crud_users.get(
        db=db, schema_to_select=UserRead, username=username, is_deleted=False
    )
    if db_user is None:
        raise NotFoundException("User not found")

    return db_user


@router.patch("/user/{username}")
async def patch_user(
    request: Request,
    values: UserUpdate,
    username: str,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    """
    Updates a user's details in the database by patching the user's data. It checks
    for existing usernames and emails, ensuring they are unique and do not belong
    to other users. It also enforces authorization and validation for the current
    user.

    Args:
        request (Request): An asynchronous parameter that represents the HTTP request.
        values (UserUpdate): Annotated with the `Depends` function, which is not
            shown in the provided code snippet. It is used to inject the UserUpdate
            object into the function.
        username (str): A path parameter extracted from the URL.
        current_user (Annotated[UserRead, Depends(get_current_user)]): Derived
            from the `get_current_user` dependency, which presumably retrieves the
            currently authenticated user.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Decorated with the
            `@Depends` decorator from FastAPI, indicating that it depends on the
            result of the `async_get_db` function, which presumably returns an
            asynchronous database session.

    Returns:
        dict[str, str]: A dictionary with a single key-value pair, where the key
        is "message" and the value is the string "User updated".

    """
    db_user = await crud_users.get(db=db, schema_to_select=UserRead, username=username)
    if db_user is None:
        raise NotFoundException("User not found")

    if db_user["username"] != current_user["username"]:
        raise ForbiddenException()

    if values.username != db_user["username"]:
        existing_username = await crud_users.exists(db=db, username=values.username)
        if existing_username:
            raise DuplicateValueException("Username not available")

    if values.email != db_user["email"]:
        existing_email = await crud_users.exists(db=db, email=values.email)
        if existing_email:
            raise DuplicateValueException("Email is already registered")

    await crud_users.update(db=db, object=values, username=username)
    return {"message": "User updated"}


@router.delete("/user/{username}")
async def erase_user(
    request: Request,
    username: str,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
    token: str = Depends(oauth2_scheme),
) -> dict[str, str]:
    """
    Handles a DELETE request to delete a user's account. It checks for the user's
    existence, verifies the user's identity, deletes the user's data, adds the
    user's token to the blacklist, and returns a success message.

    Args:
        request (Request): Required for the function to access the current request
            in an asynchronous context.
        username (str): A path parameter, extracted from the URL path of the HTTP
            request to the "/user/{username}" endpoint.
        current_user (Annotated[UserRead, Depends(get_current_user)]): Decorated
            with the `Depends` dependency injection mechanism, which means that
            it is resolved at runtime to the currently authenticated user.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Injected by the
            `async_get_db` dependency, which returns an asynchronous database session.
        token (str): Optional by default, using the `= Depends(oauth2_scheme)`
            syntax to specify a default value if not provided.

    Returns:
        dict[str, str]: A dictionary containing a single key-value pair with the
        key "message" and the value "User deleted".

    """
    db_user = await crud_users.get(db=db, schema_to_select=UserRead, username=username)
    if not db_user:
        raise NotFoundException("User not found")

    if username != current_user["username"]:
        raise ForbiddenException()

    await crud_users.delete(db=db, username=username)
    await blacklist_token(token=token, db=db)
    return {"message": "User deleted"}


@router.delete("/db_user/{username}", dependencies=[Depends(get_current_superuser)])
async def erase_db_user(
    request: Request,
    username: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    token: str = Depends(oauth2_scheme),
) -> dict[str, str]:
    """
    Deletes a database user by username, requiring a superuser to access the
    endpoint. It checks for user existence, deletes the user from the database,
    and blacklists the access token associated with the request.

    Args:
        request (Request): Required for the function. It represents the current
            HTTP request being processed.
        username (str): Path parameter, which is extracted from the URL path of
            the "/db_user/{username}" endpoint.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Injected by the
            `async_get_db` dependency, which is a function that returns an instance
            of `AsyncSession`, a database session object.
        token (str): Annotated with `Depends(oauth2_scheme)`, indicating that it
            is obtained from an OAuth 2.0 scheme.

    Returns:
        dict[str, str]: A dictionary containing a single key-value pair, where the
        key is "message" and the value is a string indicating that the user has
        been deleted from the database.

    """
    db_user = await crud_users.exists(db=db, username=username)
    if not db_user:
        raise NotFoundException("User not found")

    await crud_users.db_delete(db=db, username=username)
    await blacklist_token(token=token, db=db)
    return {"message": "User deleted from the database"}


@router.get("/user/{username}/rate_limits", dependencies=[Depends(get_current_superuser)])
async def read_user_rate_limits(
    request: Request, username: str, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, Any]:
    """
    Retrieves the rate limits for a specific user based on their tier, returning
    the user's details with their tier's rate limits. It requires a superuser to
    access this endpoint and raises exceptions if the user or tier is not found.

    Args:
        request (Request): Required to pass the current request to the function.
            This is likely used to access request-specific information such as
            headers or query parameters.
        username (str): Bound to the path parameter of the same name in the route,
            which is a path parameter that matches the value of the "username"
            part of the URL path.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Required for database
            operations. It is annotated with `AsyncSession` and `Depends(async_get_db)`,
            indicating that it depends on an asynchronous database session obtained
            through the `async_get_db` function.

    Returns:
        dict[str, Any]: A dictionary containing information about the user's rate
        limits, including their tier rate limits.

    """
    db_user: dict | None = await crud_users.get(db=db, username=username, schema_to_select=UserRead)
    if db_user is None:
        raise NotFoundException("User not found")

    if db_user["tier_id"] is None:
        db_user["tier_rate_limits"] = []
        return db_user

    db_tier = await crud_tiers.get(db=db, id=db_user["tier_id"])
    if db_tier is None:
        raise NotFoundException("Tier not found")

    db_rate_limits = await crud_rate_limits.get_multi(db=db, tier_id=db_tier["id"])

    db_user["tier_rate_limits"] = db_rate_limits["data"]

    return db_user


@router.get("/user/{username}/tier")
async def read_user_tier(
    request: Request, username: str, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict | None:
    """
    Retrieves information about a user's tier and related data from the database.
    It checks for the existence of the user and tier, and returns the user's data
    joined with their tier data if both exist.

    Args:
        request (Request): A dependency injected by the `Depends(async_get_db)`
            annotation, but it is not used within the function. It is likely a
            leftover from the function's original implementation.
        username (str): Extracted from the path of the HTTP request, denoted by
            the `{username}` path parameter in the `/user/{username}/tier` route.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Injected by the
            `Depends` annotation, which is a dependency injection system in FastAPI.
            It calls the `async_get_db` function to get an instance of `AsyncSession`
            for database operations.

    Returns:
        dict | None: A dictionary containing the joined user data with tier
        information if the user and tier exist, otherwise it returns None.

    """
    db_user = await crud_users.get(db=db, username=username, schema_to_select=UserRead)
    if db_user is None:
        raise NotFoundException("User not found")

    db_tier = await crud_tiers.exists(db=db, id=db_user["tier_id"])
    if not db_tier:
        raise NotFoundException("Tier not found")

    joined: dict = await crud_users.get_joined(
        db=db,
        join_model=Tier,
        join_prefix="tier_",
        schema_to_select=UserRead,
        join_schema_to_select=TierRead,
        username=username,
    )

    return joined


@router.patch("/user/{username}/tier", dependencies=[Depends(get_current_superuser)])
async def patch_user_tier(
    request: Request, username: str, values: UserTierUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    """
    Updates a user's tier by modifying their existing record in the database. It
    requires a superuser to make the change and ensures both the user and tier
    exist before updating the user's tier.

    Args:
        request (Request): Used to access information from the current HTTP request.
        username (str): A path parameter, derived from the URL path "/user/{username}/tier"
            where {username} is replaced with the actual username.
        values (UserTierUpdate): Defined as a schema to update a user's tier.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Used to specify the
            database session for the operation. It is obtained through dependency
            injection using the `async_get_db` function.

    Returns:
        dict[str, str]: A dictionary containing a single key-value pair with the
        key "message" and the value being a string that indicates the user's tier
        has been updated.

    """
    db_user = await crud_users.get(db=db, username=username, schema_to_select=UserRead)
    if db_user is None:
        raise NotFoundException("User not found")

    db_tier = await crud_tiers.get(db=db, id=values.tier_id)
    if db_tier is None:
        raise NotFoundException("Tier not found")

    await crud_users.update(db=db, object=values, username=username)
    return {"message": f"User {db_user['name']} Tier updated"}
