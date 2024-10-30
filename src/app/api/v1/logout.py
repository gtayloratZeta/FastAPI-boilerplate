from fastapi import APIRouter, Depends, Response
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import UnauthorizedException
from ...core.security import blacklist_token, oauth2_scheme

router = APIRouter(tags=["login"])


@router.post("/logout")
async def logout(
    response: Response, access_token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(async_get_db)
) -> dict[str, str]:
    """
    Handles a POST request to the `/logout` endpoint, revokes an access token,
    deletes a refresh token cookie, and returns a success message upon successful
    logout. It also handles invalid tokens and raises an exception if the token
    is not valid.

    Args:
        response (Response): Used to interact with the HTTP response being sent
            back to the client.
        access_token (str): Dependent on the `oauth2_scheme`, indicating that it
            is obtained through an OAuth2 scheme.
        db (AsyncSession): Dependency of the `async_get_db` function. It represents
            a database session for asynchronous database operations.

    Returns:
        dict[str, str]: A dictionary containing a single key-value pair, where the
        key is "message" and the value is a string indicating that the logout was
        successful.

    """
    try:
        await blacklist_token(token=access_token, db=db)
        response.delete_cookie(key="refresh_token")

        return {"message": "Logged out successfully"}

    except JWTError:
        raise UnauthorizedException("Invalid token.")
