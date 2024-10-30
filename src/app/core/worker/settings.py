from arq.connections import RedisSettings

from ...core.config import settings
from .functions import sample_background_task, shutdown, startup

REDIS_QUEUE_HOST = settings.REDIS_QUEUE_HOST
REDIS_QUEUE_PORT = settings.REDIS_QUEUE_PORT


class WorkerSettings:
    """
    Defines application settings for a worker process.
    It includes a list of functions to be executed, Redis settings for communication,
    and callback functions for startup and shutdown events.

    Attributes:
        functions (List[Callable]): Initialized with a list containing a single
            callable function `sample_background_task`.
        redis_settings (RedisSettings): Configured with Redis connection settings,
            including the host and port of the Redis server.
        on_startup (Callable[[],None]): Set to the function `startup`. This function
            is typically a callback that is executed when the worker starts.
        on_shutdown (callable): Typically used to define a function that is executed
            when the worker is shutting down. It is used to perform any necessary
            cleanup or tasks before the worker exits.
        handle_signals (bool): Configured to handle signals, indicating whether
            the worker should catch and handle signals sent to it, allowing it to
            perform cleanup or other necessary actions when receiving signals such
            as SIGTERM or SIGINT.

    """
    functions = [sample_background_task]
    redis_settings = RedisSettings(host=REDIS_QUEUE_HOST, port=REDIS_QUEUE_PORT)
    on_startup = startup
    on_shutdown = shutdown
    handle_signals = False
