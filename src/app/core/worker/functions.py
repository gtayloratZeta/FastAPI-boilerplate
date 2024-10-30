import asyncio
import logging

import uvloop
from arq.worker import Worker

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


# -------- background tasks --------
async def sample_background_task(ctx: Worker, name: str) -> str:
    """
    Pauses execution for 5 seconds using `asyncio.sleep` before returning a success
    message indicating the task is complete.

    Args:
        ctx (Worker): Expected to be an instance of a class that represents a
            worker, likely providing context for the task execution.
        name (str): Named `name`. It represents the name of the task being executed
            and is used to identify it in the returned message.

    Returns:
        str: A string indicating that a task with the specified name has been completed.

    """
    await asyncio.sleep(5)
    return f"Task {name} is complete!"


# -------- base functions --------
async def startup(ctx: Worker) -> None:
    logging.info("Worker Started")


async def shutdown(ctx: Worker) -> None:
    logging.info("Worker end")
