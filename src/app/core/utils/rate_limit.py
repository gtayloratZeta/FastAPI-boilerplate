from datetime import UTC, datetime

from redis.asyncio import ConnectionPool, Redis
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.logger import logging
from ...schemas.rate_limit import sanitize_path

logger = logging.getLogger(__name__)

pool: ConnectionPool | None = None
client: Redis | None = None


async def is_rate_limited(db: AsyncSession, user_id: int, path: str, limit: int, period: int) -> bool:
    """
    Checks if a user has exceeded a rate limit for a specific path within a given
    period. It uses Redis to store the count of requests and expires the key after
    the period, implementing a sliding window approach.

    Args:
        db (AsyncSession): Used to interact with a database.
        user_id (int): Used to uniquely identify a user for rate limiting purposes.
            It is used as part of the Redis key to store the rate limit information.
        path (str): A URL path or endpoint that is being rate-limited. It is
            sanitized before use to prevent potential security vulnerabilities.
        limit (int): Used to specify the maximum number of requests allowed within
            the specified time period.
        period (int): Used to determine the window of time for which the rate
            limiting is applied. It represents the number of seconds in the time
            window.

    Returns:
        bool: True if the user has exceeded the specified rate limit and False otherwise.

    """
    if client is None:
        logger.error("Redis client is not initialized.")
        raise Exception("Redis client is not initialized.")

    current_timestamp = int(datetime.now(UTC).timestamp())
    window_start = current_timestamp - (current_timestamp % period)

    sanitized_path = sanitize_path(path)
    key = f"ratelimit:{user_id}:{sanitized_path}:{window_start}"

    try:
        current_count = await client.incr(key)
        if current_count == 1:
            await client.expire(key, period)

        if current_count > limit:
            return True

    except Exception as e:
        logger.exception(f"Error checking rate limit for user {user_id} on path {path}: {e}")
        raise e

    return False
