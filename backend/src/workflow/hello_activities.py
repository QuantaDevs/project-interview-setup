from temporalio import activity


@activity.defn
async def greet(name: str) -> str:
    """
    An activity is a function that does the actual work in a Temporal workflow.
    Activities can call APIs, query databases, or perform any side-effectful operation.
    The Temporal worker executes activities and reports results back to the server.
    """
    return f"Hello, {name}!"


# ────────────────────────────────────────────────────────────────────────────────
# BONUS CHALLENGE (optional)
#
# Uncomment the activity below (and the corresponding lines in
# hello_workflow.py and run_worker.py), then click "Say Hello" again.
#
# The workflow will fail. Use the Temporal UI at http://localhost:8233 to
# inspect the failed workflow, find the error, and fix it.
# ────────────────────────────────────────────────────────────────────────────────

# @activity.defn
# async def format_greeting(greeting: str) -> str:
#     """Format a greeting with a timestamp."""
#     from datetime import datetime
#     timestamp = datetime.now().strftime("%I:%M %p")
#     return {"formatted": f"[{timestamp}] {greeting}"}
