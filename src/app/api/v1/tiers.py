from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_superuser
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ...crud.crud_tier import crud_tiers
from ...schemas.tier import TierCreate, TierCreateInternal, TierRead, TierUpdate

router = APIRouter(tags=["tiers"])


@router.post("/tier", dependencies=[Depends(get_current_superuser)], status_code=201)
async def write_tier(
    request: Request, tier: TierCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> TierRead:
    """
    Creates a new tier in the database. It checks for duplicate tier names, raises
    an exception if found, and returns the newly created tier if the name is unique.
    The function requires a superuser to make the POST request.

    Args:
        request (Request): Used to represent the HTTP request. It is annotated
            with the type `Request` and is a required parameter of the function.
        tier (TierCreate): Bound to a JSON payload from the incoming HTTP request.
            It represents a new tier to be created.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Injected by the
            `async_get_db` dependency. It is an asynchronous database session.

    Returns:
        TierRead: A representation of the newly created tier in the database.

    """
    tier_internal_dict = tier.model_dump()
    db_tier = await crud_tiers.exists(db=db, name=tier_internal_dict["name"])
    if db_tier:
        raise DuplicateValueException("Tier Name not available")

    tier_internal = TierCreateInternal(**tier_internal_dict)
    created_tier: TierRead = await crud_tiers.create(db=db, object=tier_internal)
    return created_tier


@router.get("/tiers", response_model=PaginatedListResponse[TierRead])
async def read_tiers(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10
) -> dict:
    """
    Handles GET requests to the `/tiers` endpoint, retrieving a paginated list of
    `TierRead` objects from the database and returning them in a formatted response.

    Args:
        request (Request): Required for the function. It is not explicitly used
            in the provided code snippet.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Injected into the
            function using the `Depends` annotation, indicating that it is a
            database session retrieved from the `async_get_db` function.
        page (int): Optional. It defaults to 1, indicating the first page of results.
        items_per_page (int): Defaulted to 10, specifying the number of items to
            display per page in the paginated response.

    Returns:
        dict: A paginated list of tier data in JSON format.

    """
    tiers_data = await crud_tiers.get_multi(
        db=db, offset=compute_offset(page, items_per_page), limit=items_per_page, schema_to_select=TierRead
    )

    response: dict[str, Any] = paginated_response(crud_data=tiers_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/tier/{name}", response_model=TierRead)
async def read_tier(request: Request, name: str, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict:
    """
    Handles a GET request to retrieve a specific tier by name from a database. It
    queries the database, checks if the tier exists, and raises a `NotFoundException`
    if not found; otherwise, it returns the tier data in the `TierRead` format.

    Args:
        request (Request): Used to represent the incoming HTTP request from the client.
        name (str): Path parameter, which is extracted from the URL path of the
            request. It represents the name of the tier to be read.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Dependent on the
            result of the `async_get_db` function, which is likely used to obtain
            a database session.

    Returns:
        dict: A dictionary representation of the `TierRead` object retrieved from
        the database.

    """
    db_tier: TierRead | None = await crud_tiers.get(db=db, schema_to_select=TierRead, name=name)
    if db_tier is None:
        raise NotFoundException("Tier not found")

    return db_tier


@router.patch("/tier/{name}", dependencies=[Depends(get_current_superuser)])
async def patch_tier(
    request: Request, values: TierUpdate, name: str, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    """
    Updates a tier in the database by name, requiring a superuser and returning a
    success message upon completion.

    Args:
        request (Request): A dependency of the function, which is automatically
            resolved by the FastAPI framework.
        values (TierUpdate): Bound to the data from the request body, which contains
            the updated tier information.
        name (str): A path parameter, indicating it is extracted from the URL path,
            specifically the "/tier/{name}" route.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Injected by the
            `async_get_db` dependency, which is a function that returns an
            asynchronous database session. This allows the function to interact
            with the database.

    Returns:
        dict[str, str]: A dictionary containing a single key-value pair where the
        key is "message" and the value is the string "Tier updated".

    """
    db_tier = await crud_tiers.get(db=db, schema_to_select=TierRead, name=name)
    if db_tier is None:
        raise NotFoundException("Tier not found")

    await crud_tiers.update(db=db, object=values, name=name)
    return {"message": "Tier updated"}


@router.delete("/tier/{name}", dependencies=[Depends(get_current_superuser)])
async def erase_tier(request: Request, name: str, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    """
    Deletes a tier by name. It retrieves the tier from the database, raises a
    `NotFoundException` if it does not exist, deletes the tier, and returns a
    success message upon completion.

    Args:
        request (Request): Required for the function to access information from
            the current HTTP request.
        name (str): Bound to the path parameter `name` in the route definition
            `/tier/{name}`, indicating it is a path parameter extracted from the
            URL.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Injected into the
            function through dependency injection, which means it is retrieved
            from the database using the `async_get_db` function.

    Returns:
        dict[str, str]: A dictionary containing a single key-value pair where the
        key is "message" and the value is a string indicating that the tier has
        been deleted.

    """
    db_tier = await crud_tiers.get(db=db, schema_to_select=TierRead, name=name)
    if db_tier is None:
        raise NotFoundException("Tier not found")

    await crud_tiers.delete(db=db, name=name)
    return {"message": "Tier deleted"}
