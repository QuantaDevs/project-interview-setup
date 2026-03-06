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
