# Hello World Setup Project — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** A standalone repo that validates a candidate has Git, Python, Node, Temporal, and the full stack running before their onsite interview.

**Architecture:** Next.js frontend (port 3000) proxies API calls to Flask backend (port 8000). Backend has one endpoint `/api/hello` that starts a Temporal workflow. The workflow calls a single `greet` activity and returns the result. SQLite DB auto-creates on install to validate SQLAlchemy works.

**Tech Stack:** Python 3.12+ (Flask, Temporal SDK, SQLAlchemy), Node 18+ (Next.js 13, Tailwind), uv, nodemon, Make

---

### Task 1: Backend — pyproject.toml and init_db.py

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/init_db.py`
- Create: `backend/src/__init__.py`
- Create: `backend/src/db/__init__.py`
- Create: `backend/src/db/base.py`

**Step 1: Create pyproject.toml**

```toml
[project]
name = "backend"
version = "0.1.0"
description = "Interview setup — hello world backend"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "flask[async]>=3.1.0",
    "flask-cors>=5.0.1",
    "python-dotenv>=1.1.0",
    "sqlalchemy==2.0.36",
    "temporalio>=1.10.0",
]
```

**Step 2: Create src/db/base.py**

Minimal SQLAlchemy base — just enough to prove the DB works.

```python
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

class Base(object):
    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime, default=datetime.now(timezone.utc), nullable=True
    )

BaseTable = declarative_base(cls=Base)


class Greeting(BaseTable):
    """A simple table to verify SQLAlchemy + SQLite works."""
    __tablename__ = "greetings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message: Mapped[str] = mapped_column(String(255))
```

**Step 3: Create init_db.py**

```python
import os
from sqlalchemy import create_engine
from src.db.base import BaseTable


def init_db(db_url=None):
    if db_url is None:
        db_url = os.getenv("DB_URL", "sqlite:///hello.db")
    engine = create_engine(db_url)
    BaseTable.metadata.create_all(engine)
    print(f"Database initialized at: {db_url}")


if __name__ == "__main__":
    init_db()
```

**Step 4: Create empty __init__.py files**

Create `backend/src/__init__.py` and `backend/src/db/__init__.py` (empty files).

**Step 5: Verify**

Run: `cd backend && uv sync && uv run init_db.py`
Expected: "Database initialized at: sqlite:///hello.db" and `hello.db` file created.

**Step 6: Commit**

```bash
git add backend/pyproject.toml backend/init_db.py backend/src/
git commit -m "feat: add backend project config and database init"
```

---

### Task 2: Backend — Temporal workflow and activity

**Files:**
- Create: `backend/src/workflow/__init__.py`
- Create: `backend/src/workflow/hello_activities.py`
- Create: `backend/src/workflow/hello_workflow.py`

**Step 1: Create hello_activities.py**

```python
from temporalio import activity


@activity.defn
def greet(name: str) -> str:
    """
    An activity is a function that does the actual work in a Temporal workflow.
    Activities can call APIs, query databases, or perform any side-effectful operation.
    The Temporal worker executes activities and reports results back to the server.
    """
    return f"Hello, {name}!"
```

**Step 2: Create hello_workflow.py**

```python
from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from src.workflow.hello_activities import greet


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
        return result
```

**Step 3: Create empty __init__.py**

Create `backend/src/workflow/__init__.py` (empty file).

**Step 4: Commit**

```bash
git add backend/src/workflow/
git commit -m "feat: add hello world Temporal workflow and activity"
```

---

### Task 3: Backend — Temporal worker

**Files:**
- Create: `backend/run_worker.py`

**Step 1: Create run_worker.py**

```python
import asyncio
import logging
import sys

from temporalio.client import Client
from temporalio.worker import Worker

from src.workflow.hello_activities import greet
from src.workflow.hello_workflow import HelloWorkflow


async def main():
    client = await Client.connect("localhost:7233")
    print("Connected to Temporal server")

    worker = Worker(
        client,
        task_queue="hello-task-queue",
        workflows=[HelloWorkflow],
        activities=[greet],
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
```

**Step 2: Commit**

```bash
git add backend/run_worker.py
git commit -m "feat: add Temporal worker entry point"
```

---

### Task 4: Backend — Flask app

**Files:**
- Create: `backend/app.py`

**Step 1: Create app.py**

```python
import uuid

from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from temporalio.client import Client

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

        client = await Client.connect("localhost:7233")
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
```

**Step 2: Verify**

Run: `cd backend && uv run -- flask --debug run -p 8000`
Expected: Flask starts on port 8000 without errors.

**Step 3: Commit**

```bash
git add backend/app.py
git commit -m "feat: add Flask app with /api/hello endpoint"
```

---

### Task 5: Frontend — project config

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/next.config.js`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/styles/globals.css`

**Step 1: Create package.json**

```json
{
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "lint": "next lint"
  },
  "dependencies": {
    "autoprefixer": "^10.4.13",
    "next": "^13.0.7",
    "postcss": "^8.4.20",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "tailwindcss": "^3.2.4"
  },
  "devDependencies": {
    "@types/node": "18.11.17",
    "@types/react": "18.0.26",
    "eslint": "8.30.0",
    "eslint-config-next": "13.0.7",
    "typescript": "^4.9.4"
  }
}
```

**Step 2: Create tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": false,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "incremental": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve"
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

**Step 3: Create next.config.js**

```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    unoptimized: true,
  },
  rewrites: async function () {
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
```

**Step 4: Create tailwind.config.js**

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./pages/**/*.{ts,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

**Step 5: Create postcss.config.js**

```js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

**Step 6: Create styles/globals.css**

```css
@import "tailwindcss/base";
@import "tailwindcss/components";
@import "tailwindcss/utilities";
```

**Step 7: Commit**

```bash
git add frontend/
git commit -m "feat: add frontend project config (Next.js, Tailwind)"
```

---

### Task 6: Frontend — pages

**Files:**
- Create: `frontend/pages/_app.tsx`
- Create: `frontend/pages/index.tsx`

**Step 1: Create _app.tsx**

```tsx
import type { AppProps } from "next/app";
import Head from "next/head";

import "../styles/globals.css";

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <title>Interview Setup</title>
      </Head>
      <Component {...pageProps} />
    </>
  );
}
```

**Step 2: Create index.tsx**

```tsx
import React, { useState } from "react";

export default function HomePage() {
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sayHello = async () => {
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      const res = await fetch("/api/hello", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: "World" }),
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      const data = await res.json();
      setMessage(data.message);
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">
          Interview Setup
        </h1>
        <p className="text-gray-500">
          Click the button to verify your full stack is working.
        </p>

        <button
          onClick={sayHello}
          disabled={loading}
          className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Running workflow..." : "Say Hello"}
        </button>

        {message && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-800 font-medium">{message}</p>
            <p className="text-green-600 text-sm mt-1">
              Frontend → Flask → Temporal Workflow → Activity → Response
            </p>
          </div>
        )}

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800 font-medium">Error: {error}</p>
            <p className="text-red-600 text-sm mt-1">
              Make sure all 4 processes are running (see README).
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
```

**Step 3: Commit**

```bash
git add frontend/pages/
git commit -m "feat: add frontend pages with hello world button"
```

---

### Task 7: Root — Makefile and .gitignore

**Files:**
- Create: `Makefile`
- Create: `.gitignore`

**Step 1: Create Makefile**

```makefile
.PHONY: install install-backend install-frontend run-dev run-frontend-dev run-worker check

###### Installation ######
install i: install-backend install-frontend

install-backend ib:
	@cd backend && uv sync && uv run init_db.py

install-frontend if:
	@cd frontend && npm install --include=dev

###### Services ######
run-dev rd:
	@cd backend && uv run -- flask --debug run -p 8000

run-frontend-dev rfd:
	@cd frontend && npm run dev

run-worker rw:
	@cd backend && nodemon -e py --exec uv run run_worker.py

###### Checks ######
check c:
	@echo "Python version:"
	@python3 --version
	@echo "\nNode version:"
	@node --version
	@echo "\nuv version:"
	@uv --version
	@echo "\ntemporal version:"
	@temporal --version
```

**Step 2: Create .gitignore**

```
# Python
__pycache__/
*.py[cod]
*.db
.venv/
*.egg-info/

# Node
node_modules/
.next/

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store

# uv
uv.lock
```

**Step 3: Commit**

```bash
git add Makefile .gitignore
git commit -m "feat: add Makefile and .gitignore"
```

---

### Task 8: Root — README.md

**Files:**
- Create: `README.md`

**Step 1: Create README.md**

```markdown
# Interview Setup

Welcome! This project verifies that your development environment is ready for the onsite interview. Follow the steps below to get everything running.

## Prerequisites

You'll need [Homebrew](https://brew.sh/) installed, plus:

- **Git** (you have it if you cloned this repo)
- **Python 3.12+** — check with `python3 --version`
- **Node 18+** — check with `node --version`

## Install Tools

```bash
brew install temporal uv
npm install -g nodemon
```

- **uv** manages Python packages and virtual environments (no manual venv needed)
- **temporal** runs the Temporal server locally
- **nodemon** auto-restarts the worker when Python files change

## Install Dependencies

```bash
make install
```

This installs Python and Node dependencies, and creates the SQLite database.

## Run the App

You need 4 processes running in separate terminal tabs:

```bash
# Tab 1: Temporal server
temporal server start-dev

# Tab 2: Backend (Flask on http://localhost:8000)
make run-dev

# Tab 3: Temporal worker
make run-worker

# Tab 4: Frontend (Next.js on http://localhost:3000)
make run-frontend-dev
```

## Verify

Visit [http://localhost:3000](http://localhost:3000) and click **"Say Hello"**. You should see:

> Hello, World!

If you see that, your setup is complete.

## What is Temporal?

Temporal is a workflow engine that makes it easy to build reliable applications. Here's how the pieces fit together:

- A **workflow** orchestrates a sequence of steps. It's a durable function — if the process crashes, the workflow resumes right where it left off.
- An **activity** does the actual work (API calls, database writes, etc.). Activities are called by workflows.
- A **worker** is a process that listens for tasks and executes workflows and activities.
- The **Temporal server** coordinates everything — it tracks workflow state and dispatches tasks to workers.

When you click "Say Hello", the frontend calls the Flask backend, which starts a `HelloWorkflow` on the Temporal server. The worker picks it up, runs the `greet` activity, and returns the result.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `make install` fails on Python | Make sure `python3 --version` shows 3.12+. Install via `brew install python@3.12` |
| `make install` fails on Node | Make sure `node --version` shows 18+. Install via `brew install node@18` |
| "Say Hello" shows an error | Make sure all 4 processes are running. Check each terminal for errors. |
| Worker can't connect | Make sure `temporal server start-dev` is running first. |
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "feat: add README with setup instructions"
```

---

### Task 9: Initialize git repo and final verification

**Step 1: Init git repo**

```bash
cd /Users/shivam/orepos/project-interview-setup
git init
```

**Step 2: Make initial commit with all files**

Stage and commit everything created in tasks 1-8.

**Step 3: Full end-to-end verification**

1. `make check` — verify Python, Node, uv, temporal versions print correctly
2. `make install` — verify clean install works
3. In 4 terminals: `temporal server start-dev`, `make run-dev`, `make run-worker`, `make run-frontend-dev`
4. Visit `http://localhost:3000`, click "Say Hello", confirm "Hello, World!" appears
5. Check Temporal UI at `http://localhost:8233` — verify the workflow appears as completed

**Step 4: Commit any fixes from verification**
