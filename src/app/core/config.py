import os
from enum import Enum

from pydantic_settings import BaseSettings
from starlette.config import Config

current_file_dir = os.path.dirname(os.path.realpath(__file__))
env_path = os.path.join(current_file_dir, "..", "..", ".env")
config = Config(env_path)


class AppSettings(BaseSettings):
    """
    Defines a data model for application settings. It uses environment variables
    to configure various application attributes, including name, description,
    version, license, and contact information, providing default values when these
    variables are not set.

    Attributes:
        APP_NAME (str): Initialized with the value obtained from the environment
            variable `APP_NAME`. It defaults to the string "FastAPI app" if the
            environment variable is not set.
        APP_DESCRIPTION (str | None): Configured using the `config` function from
            the `BaseSettings` class. It retrieves the value of the environment
            variable "APP_DESCRIPTION" and assigns the default value of None if
            the variable is not set.
        APP_VERSION (str | None): Configured using the `config` function from the
            `pydantic` library. It retrieves the value of the environment variable
            `APP_VERSION` or defaults to None if the variable is not set.
        LICENSE_NAME (str | None): Initialized with a value obtained from the
            environment variable named `LICENSE` using the `config` function. If
            the environment variable is not set, it defaults to None.
        CONTACT_NAME (str | None): Configured using the `config` function with the
            key "CONTACT_NAME". It has a default value of None, indicating that
            the contact name may not be provided.
        CONTACT_EMAIL (str | None): Configured using the `config` function with
            the environment variable `CONTACT_EMAIL`, having a default value of `None`.

    """
    APP_NAME: str = config("APP_NAME", default="FastAPI app")
    APP_DESCRIPTION: str | None = config("APP_DESCRIPTION", default=None)
    APP_VERSION: str | None = config("APP_VERSION", default=None)
    LICENSE_NAME: str | None = config("LICENSE", default=None)
    CONTACT_NAME: str | None = config("CONTACT_NAME", default=None)
    CONTACT_EMAIL: str | None = config("CONTACT_EMAIL", default=None)


class CryptSettings(BaseSettings):
    """
    Defines and loads settings for cryptographic operations. It uses a configuration
    library to retrieve values from an environment or configuration file, providing
    default values when necessary.

    Attributes:
        SECRET_KEY (str): Initialized with the value obtained from the environment
            variable "SECRET_KEY".
        ALGORITHM (str): Configured from an environment variable named "ALGORITHM".
            If this variable does not exist, a default value of "HS256" is used.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Configured to expire access tokens in
            the specified number of minutes. By default, it is set to 30 minutes.
        REFRESH_TOKEN_EXPIRE_DAYS (int): Configured to store the number of days a
            refresh token is valid before it expires.

    """
    SECRET_KEY: str = config("SECRET_KEY")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = config("REFRESH_TOKEN_EXPIRE_DAYS", default=7)


class DatabaseSettings(BaseSettings):
    pass


class SQLiteSettings(DatabaseSettings):
    """
    Defines a set of configuration settings for SQLite databases. It uses the
    `config` function to retrieve values from a configuration source, providing
    default values if not set.

    Attributes:
        SQLITE_URI (str): Used to store the URI for SQLite database connections.
            It is initialized with a default value of "./sql_app.db" and can be
            overridden by a configuration setting named "SQLITE_URI".
        SQLITE_SYNC_PREFIX (str): Configured using the `config` function. It
            defaults to the string "sqlite:///", which is a prefix for synchronous
            SQLite connections.
        SQLITE_ASYNC_PREFIX (str): Configured with the default value "sqlite+aiosqlite:///",
            indicating the prefix for asynchronous SQLite database connections.

    """
    SQLITE_URI: str = config("SQLITE_URI", default="./sql_app.db")
    SQLITE_SYNC_PREFIX: str = config("SQLITE_SYNC_PREFIX", default="sqlite:///")
    SQLITE_ASYNC_PREFIX: str = config("SQLITE_ASYNC_PREFIX", default="sqlite+aiosqlite:///")


class MySQLSettings(DatabaseSettings):
    """
    Provides configuration settings for a MySQL database, including username,
    password, server, port, database, and connection prefixes for synchronous and
    asynchronous connections.

    Attributes:
        MYSQL_USER (str): Initialized with the value retrieved from the `config`
            function using the key "MYSQL_USER". If no value exists for this key,
            it defaults to the string "username".
        MYSQL_PASSWORD (str): Initialized using the `config` function with the key
            `MYSQL_PASSWORD`. If the environment variable is not set, it defaults
            to the string "password".
        MYSQL_SERVER (str): Set to the value of the environment variable `MYSQL_SERVER`.
            If the variable is not set, it defaults to the string "localhost".
        MYSQL_PORT (int): Set to the value obtained from the `config` function,
            which retrieves the value of the "MYSQL_PORT" environment variable.
            If the variable is not set, it defaults to 5432.
        MYSQL_DB (str): Configured to store the database name for a MySQL database.
            It is retrieved from environment variables using the `config` function
            with a default value of "dbname".
        MYSQL_URI (str): Constructed as a string combining the user, password,
            server, port, and database name using the `f-string` syntax. It
            represents the connection string for a MySQL database.
        MYSQL_SYNC_PREFIX (str): Defined by the `config` function. It defaults to
            the string "mysql://".
        MYSQL_ASYNC_PREFIX (str): Configured through the `config` function with a
            default value of "mysql+aiomysql://". It appears to be a prefix for
            an asynchronous MySQL connection URL.
        MYSQL_URL (str): Configured using the `config` function. It defaults to
            None and is not explicitly used in the code snippet provided.

    """
    MYSQL_USER: str = config("MYSQL_USER", default="username")
    MYSQL_PASSWORD: str = config("MYSQL_PASSWORD", default="password")
    MYSQL_SERVER: str = config("MYSQL_SERVER", default="localhost")
    MYSQL_PORT: int = config("MYSQL_PORT", default=5432)
    MYSQL_DB: str = config("MYSQL_DB", default="dbname")
    MYSQL_URI: str = f"{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_SERVER}:{MYSQL_PORT}/{MYSQL_DB}"
    MYSQL_SYNC_PREFIX: str = config("MYSQL_SYNC_PREFIX", default="mysql://")
    MYSQL_ASYNC_PREFIX: str = config("MYSQL_ASYNC_PREFIX", default="mysql+aiomysql://")
    MYSQL_URL: str = config("MYSQL_URL", default=None)


class PostgresSettings(DatabaseSettings):
    """
    Stores and configures database settings for a Postgres database. It retrieves
    configuration values from environment variables and sets default values if not
    found. These settings are used to construct a database URI for synchronous and
    asynchronous connections.

    Attributes:
        POSTGRES_USER (str): Initialized with the value returned by the `config`
            function, which retrieves the value of the environment variable
            `POSTGRES_USER`. If the variable is not set, it defaults to the string
            `"postgres"`.
        POSTGRES_PASSWORD (str): Assigned the value of a configuration variable
            named `POSTGRES_PASSWORD`. If this variable is not provided, it defaults
            to the string `"postgres"`.
        POSTGRES_SERVER (str): Configured using the `config` function with the
            default value "localhost". This is the hostname or IP address of the
            Postgres server.
        POSTGRES_PORT (int): Configured using the `config` function with the key
            "POSTGRES_PORT" and a default value of 5432, which is the standard
            port number for PostgreSQL.
        POSTGRES_DB (str): Defined as a configuration variable named `POSTGRES_DB`
            with a default value of `"postgres"`.
        POSTGRES_SYNC_PREFIX (str): Configured using the `config` function with
            the key "POSTGRES_SYNC_PREFIX" and a default value of "postgresql://".
        POSTGRES_ASYNC_PREFIX (str): Configured through the `config` function from
            the `config` module. It defaults to the string "postgresql+asyncpg://",
            which appears to be a prefix for a PostgreSQL asynchronous connection
            URL.
        POSTGRES_URI (str): Constructed by combining the `POSTGRES_USER`,
            `POSTGRES_PASSWORD`, `POSTGRES_SERVER`, `POSTGRES_PORT`, and `POSTGRES_DB`
            attributes into a PostgreSQL connection string.
        POSTGRES_URL (str | None): Configured via the `config` function with a
            default value of None.

    """
    POSTGRES_USER: str = config("POSTGRES_USER", default="postgres")
    POSTGRES_PASSWORD: str = config("POSTGRES_PASSWORD", default="postgres")
    POSTGRES_SERVER: str = config("POSTGRES_SERVER", default="localhost")
    POSTGRES_PORT: int = config("POSTGRES_PORT", default=5432)
    POSTGRES_DB: str = config("POSTGRES_DB", default="postgres")
    POSTGRES_SYNC_PREFIX: str = config("POSTGRES_SYNC_PREFIX", default="postgresql://")
    POSTGRES_ASYNC_PREFIX: str = config("POSTGRES_ASYNC_PREFIX", default="postgresql+asyncpg://")
    POSTGRES_URI: str = f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    POSTGRES_URL: str | None = config("POSTGRES_URL", default=None)


class FirstUserSettings(BaseSettings):
    """
    Defines a data model for user settings, specifically for an admin user. It
    provides default values for admin name, email, username, and password, which
    are retrieved from environment variables using the `config` function.

    Attributes:
        ADMIN_NAME (str): Configured from an environment variable named `ADMIN_NAME`.
            If the variable is not set, it defaults to the string `"admin"`.
        ADMIN_EMAIL (str): Configured using the `config` function from the `pydantic`
            library. It retrieves the value of the ADMIN_EMAIL environment variable,
            and if the variable is not set, it defaults to "admin@admin.com".
        ADMIN_USERNAME (str): Configured with the environment variable `ADMIN_USERNAME`
            and defaults to `"admin"` if the variable is not set.
        ADMIN_PASSWORD (str): Configured with a default password of "!Ch4ng3Th1sP4ssW0rd!"
            using the `config` method, which retrieves the value from environment
            variables or a configuration file.

    """
    ADMIN_NAME: str = config("ADMIN_NAME", default="admin")
    ADMIN_EMAIL: str = config("ADMIN_EMAIL", default="admin@admin.com")
    ADMIN_USERNAME: str = config("ADMIN_USERNAME", default="admin")
    ADMIN_PASSWORD: str = config("ADMIN_PASSWORD", default="!Ch4ng3Th1sP4ssW0rd!")


class TestSettings(BaseSettings):
    ...


class RedisCacheSettings(BaseSettings):
    """
    Configures Redis cache settings by loading host and port from environment
    variables and generating a Redis URL.

    Attributes:
        REDIS_CACHE_HOST (str): Configured using the `config` function from the
            `pydantic` library. It retrieves the value of the environment variable
            `REDIS_CACHE_HOST` with a default value of "localhost".
        REDIS_CACHE_PORT (int): Configured to store the Redis server port number,
            with a default value of 6379.
        REDIS_CACHE_URL (str): Constructed using an f-string, combining the Redis
            protocol with the values of `REDIS_CACHE_HOST` and `REDIS_CACHE_PORT`
            to form a URL for Redis cache connection.

    """
    REDIS_CACHE_HOST: str = config("REDIS_CACHE_HOST", default="localhost")
    REDIS_CACHE_PORT: int = config("REDIS_CACHE_PORT", default=6379)
    REDIS_CACHE_URL: str = f"redis://{REDIS_CACHE_HOST}:{REDIS_CACHE_PORT}"


class ClientSideCacheSettings(BaseSettings):
    CLIENT_CACHE_MAX_AGE: int = config("CLIENT_CACHE_MAX_AGE", default=60)


class RedisQueueSettings(BaseSettings):
    """
    Configures settings for a Redis queue. It uses the `config` method from the
    `BaseSettings` class to retrieve environment variables for Redis host and port,
    with default values set to "localhost" and 6379, respectively.

    Attributes:
        REDIS_QUEUE_HOST (str): Configured using the `config` decorator from the
            `pydantic` library, which retrieves its value from an environment
            variable named `REDIS_QUEUE_HOST` with a default value of "localhost"
            if not set.
        REDIS_QUEUE_PORT (int): Configured by the `config` function from the
            `pydantic` library, which retrieves its value from an environment
            variable named `REDIS_QUEUE_PORT` with a default value of 6379.

    """
    REDIS_QUEUE_HOST: str = config("REDIS_QUEUE_HOST", default="localhost")
    REDIS_QUEUE_PORT: int = config("REDIS_QUEUE_PORT", default=6379)


class RedisRateLimiterSettings(BaseSettings):
    """
    Stores Redis connection settings, obtaining host and port from environment
    variables and defaulting to "localhost" and 6379 if not set. It also constructs
    the Redis URL based on the host and port.

    Attributes:
        REDIS_RATE_LIMIT_HOST (str): Configured to retrieve its value from an
            environment variable named `REDIS_RATE_LIMIT_HOST`. If the variable
            is not set, it defaults to the string "localhost".
        REDIS_RATE_LIMIT_PORT (int): Configured through the `config` method, which
            retrieves the value of the environment variable `REDIS_RATE_LIMIT_PORT`
            with a default value of 6379.
        REDIS_RATE_LIMIT_URL (str): Constructed by combining a string prefix
            "redis://" with the values of `REDIS_RATE_LIMIT_HOST` and
            `REDIS_RATE_LIMIT_PORT` attributes.

    """
    REDIS_RATE_LIMIT_HOST: str = config("REDIS_RATE_LIMIT_HOST", default="localhost")
    REDIS_RATE_LIMIT_PORT: int = config("REDIS_RATE_LIMIT_PORT", default=6379)
    REDIS_RATE_LIMIT_URL: str = f"redis://{REDIS_RATE_LIMIT_HOST}:{REDIS_RATE_LIMIT_PORT}"


class DefaultRateLimitSettings(BaseSettings):
    """
    Defines default rate limit settings using the `BaseSettings` class. It retrieves
    the default limit and period from environment variables `DEFAULT_RATE_LIMIT_LIMIT`
    and `DEFAULT_RATE_LIMIT_PERIOD`, with default values of 10 and 3600 seconds respectively.

    Attributes:
        DEFAULT_RATE_LIMIT_LIMIT (int): Configured through the `config` function,
            which retrieves a value from the environment variable `DEFAULT_RATE_LIMIT_LIMIT`
            with a default value of 10 if it is not set.
        DEFAULT_RATE_LIMIT_PERIOD (int): Configured to store the default rate limit
            period in seconds, with a default value of 3600 (1 hour).

    """
    DEFAULT_RATE_LIMIT_LIMIT: int = config("DEFAULT_RATE_LIMIT_LIMIT", default=10)
    DEFAULT_RATE_LIMIT_PERIOD: int = config("DEFAULT_RATE_LIMIT_PERIOD", default=3600)


class EnvironmentOption(Enum):
    """
    Defines a set of named values that represent different environment options,
    specifically local, staging, and production, using the `Enum` class and string
    values.

    Attributes:
        LOCAL (str): Assigned the value "local". It represents a local environment
            option, indicating that an application or system is running on a local
            machine.
        STAGING (str): Equivalent to the string "staging".
        PRODUCTION (str): Set to the string value "production", indicating a
            production environment.

    """
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentSettings(BaseSettings):
    ENVIRONMENT: EnvironmentOption = config("ENVIRONMENT", default="local")


class Settings(
    AppSettings,
    PostgresSettings,
    CryptSettings,
    FirstUserSettings,
    TestSettings,
    RedisCacheSettings,
    ClientSideCacheSettings,
    RedisQueueSettings,
    RedisRateLimiterSettings,
    DefaultRateLimitSettings,
    EnvironmentSettings,
):
    """
    Inherits multiple settings classes, combining their attributes into a single
    class, allowing for a unified access point to various application settings,
    such as database, encryption, caching, rate limiting, and environment-specific
    configurations.

    """
    pass


settings = Settings()
