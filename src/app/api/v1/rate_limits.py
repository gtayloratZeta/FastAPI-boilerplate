from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_superuser
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, NotFoundException, RateLimitException
from ...crud.crud_rate_limit import crud_rate_limits
from ...crud.crud_tier import crud_tiers
from ...schemas.rate_limit import RateLimitCreate, RateLimitCreateInternal, RateLimitRead, RateLimitUpdate

router = APIRouter(tags=["rate_limits"])


@router.post("/tier/{tier_name}/rate_limit", dependencies=[Depends(get_current_superuser)], status_code=201)
async def write_rate_limit(
    request: Request, tier_name: str, rate_limit: RateLimitCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> RateLimitRead:
    """
    Creates a new rate limit for a specified tier in a database. It first retrieves
    the tier by name, then checks if a rate limit with the same name already exists.
    If not, it creates a new rate limit and returns it.

    Args:
        request (Request): Used to obtain the current request object. It is decorated
            with the `Request` type hint.
        tier_name (str): A path parameter of the router, indicating the name of
            the tier for which a rate limit is being created.
        rate_limit (RateLimitCreate): Passed as part of the function's signature.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Injected by the
            `async_get_db` dependency. It represents an asynchronous database
            session, which is used to execute database operations.

    Returns:
        RateLimitRead: An object representing the newly created rate limit.

    """
    db_tier = await crud_tiers.get(db=db, name=tier_name)
    if not db_tier:
        raise NotFoundException("Tier not found")

    rate_limit_internal_dict = rate_limit.model_dump()
    rate_limit_internal_dict["tier_id"] = db_tier["id"]

    db_rate_limit = await crud_rate_limits.exists(db=db, name=rate_limit_internal_dict["name"])
    if db_rate_limit:
        raise DuplicateValueException("Rate Limit Name not available")

    rate_limit_internal = RateLimitCreateInternal(**rate_limit_internal_dict)
    created_rate_limit: RateLimitRead = await crud_rate_limits.create(db=db, object=rate_limit_internal)
    return created_rate_limit


@router.get("/tier/{tier_name}/rate_limits", response_model=PaginatedListResponse[RateLimitRead])
async def read_rate_limits(
    request: Request,
    tier_name: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = 1,
    items_per_page: int = 10,
) -> dict:
    """
    Retrieves a paginated list of rate limits for a specific tier from the database.
    It takes a tier name, page number, and items per page as input, and returns a
    dictionary containing the rate limits data.

    Args:
        request (Request): Used to access information about the current HTTP request.
        tier_name (str): Defined as a path parameter in the function's route. It
            represents the tier name specified in the URL of the request.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Required for database
            operations. It is obtained from the `async_get_db` dependency.
        page (int): Optional, defaulting to 1. It represents the current page
            number in a paginated response.
        items_per_page (int): Optional, defaulting to 10, and is used to specify
            the number of rate limit items to be returned per page in the response.

    Returns:
        dict: A paginated list of rate limit data, represented as a dictionary
        with keys for the current page, total pages, items per page, and the list
        of rate limit objects.

    """
    db_tier = await crud_tiers.get(db=db, name=tier_name)
    if not db_tier:
        raise NotFoundException("Tier not found")

    rate_limits_data = await crud_rate_limits.get_multi(
        db=db,
        offset=compute_offset(page, items_per_page),
        limit=items_per_page,
        schema_to_select=RateLimitRead,
        tier_id=db_tier["id"],
    )

    response: dict[str, Any] = paginated_response(crud_data=rate_limits_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/tier/{tier_name}/rate_limit/{id}", response_model=RateLimitRead)
async def read_rate_limit(
    request: Request, tier_name: str, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict:
    """
    Retrieves a rate limit by tier name and ID from a database, returning the rate
    limit data if found, or raising a `NotFoundException` if the tier or rate limit
    does not exist.

    Args:
        request (Request): A FastAPI request object that is automatically provided
            by the router and contains information about the current HTTP request.
        tier_name (str): A path parameter extracted from the URL
            "/tier/{tier_name}/rate_limit/{id}" during the request.
        id (int): Used to identify a specific rate limit within a tier.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Injected by the
            `async_get_db` dependency through the `Depends` annotation, providing
            an instance of `AsyncSession` for database operations.

    Returns:
        dict: The rate limit data read from the database for a given tier and ID.

    """
    db_tier = await crud_tiers.get(db=db, name=tier_name)
    if not db_tier:
        raise NotFoundException("Tier not found")

    db_rate_limit: dict | None = await crud_rate_limits.get(
        db=db, schema_to_select=RateLimitRead, tier_id=db_tier["id"], id=id
    )
    if db_rate_limit is None:
        raise NotFoundException("Rate Limit not found")

    return db_rate_limit


@router.patch("/tier/{tier_name}/rate_limit/{id}", dependencies=[Depends(get_current_superuser)])
async def patch_rate_limit(
    request: Request,
    tier_name: str,
    id: int,
    values: RateLimitUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    """
    Updates a rate limit for a specific tier and path, allowing a superuser to
    modify or add a rate limit with unique path and name. It checks for existing
    rate limits and raises exceptions if they already exist.

    Args:
        request (Request): Used to access the data from the HTTP request.
        tier_name (str): Extracted from the URL path as a path parameter named
            {tier_name}. It represents the name of a tier for which rate limit is
            being updated.
        id (int): Used to identify a specific rate limit to be updated.
        values (RateLimitUpdate): Used to update a rate limit. It is expected to
            contain the new values for the rate limit being updated.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Awaited to retrieve
            an AsyncSession from the database using the `async_get_db` dependency.

    Returns:
        dict[str, str]: A dictionary containing a single key-value pair with the
        key "message" and the value "Rate Limit updated".

    """
    db_tier = await crud_tiers.get(db=db, name=tier_name)
    if db_tier is None:
        raise NotFoundException("Tier not found")

    db_rate_limit = await crud_rate_limits.get(db=db, schema_to_select=RateLimitRead, tier_id=db_tier["id"], id=id)
    if db_rate_limit is None:
        raise NotFoundException("Rate Limit not found")

    db_rate_limit_path = await crud_rate_limits.exists(db=db, tier_id=db_tier["id"], path=values.path)
    if db_rate_limit_path:
        raise DuplicateValueException("There is already a rate limit for this path")

    await crud_rate_limits.exists(db=db)
    if db_rate_limit_path:
        raise DuplicateValueException("There is already a rate limit with this name")

    await crud_rate_limits.update(db=db, object=values, id=db_rate_limit["id"])
    return {"message": "Rate Limit updated"}


@router.delete("/tier/{tier_name}/rate_limit/{id}", dependencies=[Depends(get_current_superuser)])
async def erase_rate_limit(
    request: Request, tier_name: str, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    """
    Deletes a rate limit associated with a specific tier, accessible only by a
    superuser. It retrieves the tier and rate limit from the database, checks for
    existence, and then removes the rate limit upon successful validation.

    Args:
        request (Request): An asynchronous parameter that represents the current
            HTTP request. It is used to access request data and perform operations
            on the request.
        tier_name (str): A path parameter, extracted from the URL path where the
            route is defined as `/tier/{tier_name}/rate_limit/{id}`. It represents
            the name of a tier.
        id (int): Used to identify a specific rate limit to be deleted. It is
            passed as a path parameter to the route `/tier/{tier_name}/rate_limit/{id}`.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Used to establish a
            database connection. It is obtained by calling the `async_get_db`
            dependency function.

    Returns:
        dict[str, str]: A dictionary with a single key-value pair, where the key
        is "message" and the value is a string indicating that the rate limit has
        been deleted.

    """
    db_tier = await crud_tiers.get(db=db, name=tier_name)
    if not db_tier:
        raise NotFoundException("Tier not found")

    db_rate_limit = await crud_rate_limits.get(db=db, schema_to_select=RateLimitRead, tier_id=db_tier["id"], id=id)
    if db_rate_limit is None:
        raise NotFoundException("Rate Limit not found")

    await crud_rate_limits.delete(db=db, id=db_rate_limit["id"])
    return {"message": "Rate Limit deleted"}
