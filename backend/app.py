import uuid

from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter

from init_db import init_db
from src.workflow.hello_workflow import HelloWorkflow


def create_app():
    app = Flask(__name__)
    CORS(app)

    init_db()

    @app.route("/health")
    def health():
        return Response("OK", status=200)

    @app.route("/api/hello", methods=["POST"])
    async def hello():
        """Start a HelloWorkflow and return the result."""
        body = request.get_json(silent=True) or {}
        name = body.get("name", "World")

        client = await Client.connect(
            "localhost:7233",
            data_converter=pydantic_data_converter,
        )
        workflow_id = f"hello-{uuid.uuid4()}"

        result = await client.execute_workflow(
            HelloWorkflow.run,
            name,
            id=workflow_id,
            task_queue="hello-task-queue",
        )

        return jsonify({"message": result, "workflow_id": workflow_id})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=8000)
