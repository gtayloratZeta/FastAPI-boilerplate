from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import bcrypt
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from ..crud.crud_users import crud_users
from .config import settings
from .db.crud_token_blacklist import crud_token_blacklist
from .schemas import TokenBlacklistCreate, TokenData

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compares a given plaintext password with a hashed password to determine if
    they match. It uses the `bcrypt` library to check the password and returns a
    boolean indicating whether the passwords are valid.

    Args:
        plain_password (str): Expected to be the actual password entered by the
            user, which is compared to the hashed password.
        hashed_password (str): Representing a hashed version of a password, which
            is a fixed-size string generated from a password using a one-way hashing
            algorithm.

    Returns:
        bool: True if the provided plain password matches the hashed password,
        False otherwise, indicating whether the password is correct or not.

    """
    correct_password: bool = bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    return correct_password


def get_password_hash(password: str) -> str:
    """
    Takes a string password as input, generates a salt value using the `bcrypt.gensalt()`
    function, hashes the password using the generated salt and the `bcrypt.hashpw()`
    function, and returns the resulting hashed password as a string.

    Args:
        password (str): Required. It expects a string containing the password to
            be hashed.

    Returns:
        str: A hashed representation of the input password, generated using the
        bcrypt library.

    """
    hashed_password: str = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    return hashed_password


async def authenticate_user(username_or_email: str, password: str, db: AsyncSession) -> dict[str, Any] | Literal[False]:
    """
    Checks if a user exists in the database based on provided username or email
    and password, and returns the user's data if authentication is successful, or
    `False` otherwise.

    Args:
        username_or_email (str): Used to represent either a username or an email
            address of the user to be authenticated.
        password (str): Used to verify the password of the user being authenticated.
            It is compared to the hashed password stored in the database using the
            `verify_password` function.
        db (AsyncSession): Used to interact with a database, specifically to
            retrieve user data from the database.

    Returns:
        dict[str, Any] | Literal[False]: Either a dictionary containing user data
        or the boolean value False.

    """
    if "@" in username_or_email:
        db_user: dict | None = await crud_users.get(db=db, email=username_or_email, is_deleted=False)
    else:
        db_user = await crud_users.get(db=db, username=username_or_email, is_deleted=False)

    if not db_user:
        return False

    elif not await verify_password(password, db_user["hashed_password"]):
        return False

    return db_user


async def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Generates a JSON Web Token (JWT) based on the provided data, adding an expiration
    time if specified, and returns it as a string.

    Args:
        data (dict[str, Any]): Used to encode the payload of the JWT token. It is
            a dictionary where keys are string values and values can be of any type.
        expires_delta (timedelta | None): Optional. It represents the time delta
            after which the access token will expire, allowing for custom expiration
            times.

    Returns:
        str: A JSON Web Token (JWT) that contains the encoded data and an expiration
        time.

    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC).replace(tzinfo=None) + expires_delta
    else:
        expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Generates a JSON Web Token (JWT) for refreshing access tokens. It encodes the
    provided data with an expiration time, determined by either a specified
    `expires_delta` or a default duration.

    Args:
        data (dict[str, Any]): Required. It contains key-value pairs that are used
            to create a JSON Web Token (JWT). The keys are strings and the values
            can be of any type.
        expires_delta (timedelta | None): Optional for specifying the time delta
            after which the token expires.

    Returns:
        str: The encoded JWT token.

    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC).replace(tzinfo=None) + expires_delta
    else:
        expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_token(token: str, db: AsyncSession) -> TokenData | None:
    """Verify a JWT token and return TokenData if valid.

    Parameters
    ----------
    token: str
        The JWT token to be verified.
    db: AsyncSession
        Database session for performing database operations.

    Returns
    -------
    TokenData | None
        TokenData instance if the token is valid, None otherwise.
    """
    is_blacklisted = await crud_token_blacklist.exists(db, token=token)
    if is_blacklisted:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username_or_email: str = payload.get("sub")
        if username_or_email is None:
            return None
        return TokenData(username_or_email=username_or_email)

    except JWTError:
        return None


async def blacklist_token(token: str, db: AsyncSession) -> None:
    """
    Decodes a given JWT token to determine its expiration time and adds it to a
    database blacklist, marking it as invalid for future authentication attempts.

    Args:
        token (str): Used to represent a JSON Web Token (JWT) that is to be
            blacklisted in the database.
        db (AsyncSession): Used to interact with the database. It is likely an
            asynchronous session object that allows database operations to be
            performed in an asynchronous manner.

    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    expires_at = datetime.fromtimestamp(payload.get("exp"))
    await crud_token_blacklist.create(db, object=TokenBlacklistCreate(**{"token": token, "expires_at": expires_at}))
