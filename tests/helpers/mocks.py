from typing import Any

from fastapi.encoders import jsonable_encoder

from src.app import models
from tests.conftest import fake


def get_current_user(user: models.User) -> dict[str, Any]:
    return jsonable_encoder(user)


def oauth2_scheme() -> str:
    """
    Generates a random OAuth2 token using the SHA256 algorithm and converts it to
    a string.

    Returns:
        str: A 64-character hexadecimal string generated randomly by the `fake.sha256()`
        function.

    """
    token = fake.sha256()
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token  # type: ignore
