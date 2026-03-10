import asyncio
import logging
import sys

from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.worker import Worker

from src.workflow.hello_activities import greet
# from src.workflow.hello_activities import format_greeting  # BONUS CHALLENGE
from src.workflow.hello_workflow import HelloWorkflow


async def main():
    client = await Client.connect(
        "localhost:7233",
        data_converter=pydantic_data_converter,
    )
    print("Connected to Temporal server")

    worker = Worker(
        client,
        task_queue="hello-task-queue",
        workflows=[HelloWorkflow],
        activities=[
            greet,
            # format_greeting,  # BONUS CHALLENGE
        ],
    )
    print("Worker started, listening on 'hello-task-queue'")
    await worker.run()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(levelname)s %(asctime)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        loop.run_until_complete(loop.shutdown_asyncgens())
