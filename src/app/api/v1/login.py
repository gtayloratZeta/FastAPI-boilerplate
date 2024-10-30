from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import UnauthorizedException
from ...core.schemas import Token
from ...core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_token,
)

router = APIRouter(tags=["login"])


@router.post("/login", response_model=Token)
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    """
    Verifies user credentials, generates access and refresh tokens upon successful
    authentication, and sets the refresh token in a secure cookie with a specified
    expiration time.

    Args:
        response (Response): Used to set the response cookies, specifically the
            refresh token cookie.
        form_data (Annotated[OAuth2PasswordRequestForm, Depends()]): Annotated
            with OAuth2PasswordRequestForm, indicating it is a form data object
            that conforms to the OAuth 2.0 password request form schema, and it
            is a dependency that must be resolved.
        db (Annotated[AsyncSession, Depends(async_get_db)]): Injected by the
            `async_get_db` dependency.

    Returns:
        dict[str, str]: A dictionary containing two key-value pairs: "access_token"
        and "token_type", where "access_token" holds the access token and "token_type"
        is set to "bearer".

    """
    user = await authenticate_user(username_or_email=form_data.username, password=form_data.password, db=db)
    if not user:
        raise UnauthorizedException("Wrong username, email or password.")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)

    refresh_token = await create_refresh_token(data={"sub": user["username"]})
    max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    response.set_cookie(
        key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="Lax", max_age=max_age
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh")
async def refresh_access_token(request: Request, db: AsyncSession = Depends(async_get_db)) -> dict[str, str]:
    """
    Validates a refresh token, verifies the user's identity, and returns a new
    access token, which can be used for subsequent API requests.

    Args:
        request (Request): Used to access the HTTP request object, specifically
            to retrieve the refresh token from the cookies.
        db (AsyncSession): Dependent on the `async_get_db` function, which is
            likely a dependency injection setup to provide a database session for
            the function.

    Returns:
        dict[str, str]: A dictionary containing two key-value pairs: "access_token"
        and "token_type" with values of type str.

    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise UnauthorizedException("Refresh token missing.")

    user_data = await verify_token(refresh_token, db)
    if not user_data:
        raise UnauthorizedException("Invalid refresh token.")

    new_access_token = await create_access_token(data={"sub": user_data.username_or_email})
    return {"access_token": new_access_token, "token_type": "bearer"}
