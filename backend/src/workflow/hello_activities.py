from temporalio import activity


@activity.defn
def greet(name: str) -> str:
    """
    An activity is a function that does the actual work in a Temporal workflow.
    Activities can call APIs, query databases, or perform any side-effectful operation.
    The Temporal worker executes activities and reports results back to the server.
    """
    return f"Hello, {name}!"
