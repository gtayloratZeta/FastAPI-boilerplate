from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.db.database import async_get_db
from ..core.exceptions.http_exceptions import ForbiddenException, RateLimitException, UnauthorizedException
from ..core.logger import logging
from ..core.security import oauth2_scheme, verify_token
from ..core.utils.rate_limit import is_rate_limited
from ..crud.crud_rate_limit import crud_rate_limits
from ..crud.crud_tier import crud_tiers
from ..crud.crud_users import crud_users
from ..models.user import User
from ..schemas.rate_limit import sanitize_path

logger = logging.getLogger(__name__)

DEFAULT_LIMIT = settings.DEFAULT_RATE_LIMIT_LIMIT
DEFAULT_PERIOD = settings.DEFAULT_RATE_LIMIT_PERIOD


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, Any] | None:
    """
    Authenticates a user based on a provided token, retrieves the user's data from
    the database, and returns the user's information if authenticated successfully.

    Args:
        token (Annotated[str, Depends(oauth2_scheme)]): Annotated with two pieces
            of information: its type is a string (`str`) and it depends on the `oauth2_scheme`.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Dependent on the
            `async_get_db` function to provide an instance of `AsyncSession`.

    Returns:
        dict[str, Any] | None: A dictionary containing user information or None
        if the user is not authenticated.

    """
    token_data = await verify_token(token, db)
    if token_data is None:
        raise UnauthorizedException("User not authenticated.")

    if "@" in token_data.username_or_email:
        user: dict | None = await crud_users.get(db=db, email=token_data.username_or_email, is_deleted=False)
    else:
        user = await crud_users.get(db=db, username=token_data.username_or_email, is_deleted=False)

    if user:
        return user

    raise UnauthorizedException("User not authenticated.")


async def get_optional_user(request: Request, db: AsyncSession = Depends(async_get_db)) -> dict | None:
    """
    Verifies the presence of an "Authorization" header in the request, extracts a
    Bearer token, and uses it to authenticate the user. It returns the authenticated
    user's data if successful, or None if authentication fails or is missing.

    Args:
        request (Request): Expected to be an incoming HTTP request from a client,
            typically obtained through a web framework such as FastAPI.
        db (AsyncSession): Dependent on a function named `async_get_db`.

    Returns:
        dict | None: Either a dictionary containing user data or None if the user
        is not authenticated or an error occurs.

    """
    token = request.headers.get("Authorization")
    if not token:
        return None

    try:
        token_type, _, token_value = token.partition(" ")
        if token_type.lower() != "bearer" or not token_value:
            return None

        token_data = await verify_token(token_value, db)
        if token_data is None:
            return None

        return await get_current_user(token_value, db=db)

    except HTTPException as http_exc:
        if http_exc.status_code != 401:
            logger.error(f"Unexpected HTTPException in get_optional_user: {http_exc.detail}")
        return None

    except Exception as exc:
        logger.error(f"Unexpected error in get_optional_user: {exc}")
        return None


async def get_current_superuser(current_user: Annotated[dict, Depends(get_current_user)]) -> dict:
    """
    Checks if the current user has superuser privileges, and if they do, returns
    their details. If not, it raises a ForbiddenException.

    Args:
        current_user (Annotated[dict, Depends(get_current_user)]): Annotated with
            `Depends(get_current_user)`, indicating that it depends on the
            `get_current_user` function to resolve its value. The resolved value
            is expected to be a dictionary.

    Returns:
        dict: The current user object, assuming the current user has sufficient privileges.

    """
    if not current_user["is_superuser"]:
        raise ForbiddenException("You do not have enough privileges.")

    return current_user


async def rate_limiter(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)], user: User | None = Depends(get_optional_user)
) -> None:
    """
    Checks if a request exceeds rate limits based on user tier and path. It retrieves
    the user's tier and rate limit settings, then determines if the request is
    within the allowed limit. If not, it raises a `RateLimitException`.

    Args:
        request (Request): Used to access information about the current HTTP
            request, such as its URL path.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Scoped by the Depends
            decorator, meaning it is provided by the async_get_db function. It
            represents an asynchronous database session.
        user (User | None): Optional, with a default value provided by the
            `get_optional_user` dependency. It represents a user object, but can
            be None if no user is authenticated.

    """
    path = sanitize_path(request.url.path)
    if user:
        user_id = user["id"]
        tier = await crud_tiers.get(db, id=user["tier_id"])
        if tier:
            rate_limit = await crud_rate_limits.get(db=db, tier_id=tier["id"], path=path)
            if rate_limit:
                limit, period = rate_limit["limit"], rate_limit["period"]
            else:
                logger.warning(
                    f"User {user_id} with tier '{tier['name']}' has no specific rate limit for path '{path}'. \
                        Applying default rate limit."
                )
                limit, period = DEFAULT_LIMIT, DEFAULT_PERIOD
        else:
            logger.warning(f"User {user_id} has no assigned tier. Applying default rate limit.")
            limit, period = DEFAULT_LIMIT, DEFAULT_PERIOD
    else:
        user_id = request.client.host
        limit, period = DEFAULT_LIMIT, DEFAULT_PERIOD

    is_limited = await is_rate_limited(db=db, user_id=user_id, path=path, limit=limit, period=period)
    if is_limited:
        raise RateLimitException("Rate limit exceeded.")
