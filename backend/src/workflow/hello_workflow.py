from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from src.workflow.hello_activities import greet
    # from src.workflow.hello_activities import format_greeting  # BONUS CHALLENGE


@workflow.defn
class HelloWorkflow:
    """
    A workflow is a durable function that orchestrates activities.
    Temporal ensures workflows run to completion — even if the worker crashes,
    the workflow picks up right where it left off. Workflows should not have
    side effects; all side effects belong in activities.
    """

    @workflow.run
    async def run(self, name: str) -> str:
        result = await workflow.execute_activity(
            greet,
            name,
            start_to_close_timeout=timedelta(seconds=5),
        )

        # BONUS CHALLENGE: uncomment the lines below
        # result = await workflow.execute_activity(
        #     format_greeting,
        #     result,
        #     start_to_close_timeout=timedelta(seconds=5),
        # )

        return result
