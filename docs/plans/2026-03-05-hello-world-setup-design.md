# Hello World Setup Project Design

## Goal

A standalone repo that validates a candidate has Git, Python, Node, Temporal, and the full stack running before their onsite interview. The README doubles as their setup guide.

## What the candidate does

1. Clone the repo (validates Git)
2. `brew install temporal uv` + `npm install -g nodemon`
3. `make install` (installs Python + Node deps, auto-creates SQLite DB)
4. Start 4 processes: Temporal server, Flask backend, Temporal worker, Next.js frontend
5. Visit `localhost:3000`, see a page with a "Say Hello" button
6. Click it: frontend → Flask → Temporal workflow → activity → response displayed
7. Done. Everything works.

## Structure

```
project-interview-setup/
├── README.md
├── Makefile
├── backend/
│   ├── pyproject.toml
│   ├── app.py
│   ├── init_db.py
│   ├── run_worker.py
│   └── src/
│       └── workflow/
│           ├── hello_workflow.py
│           └── hello_activities.py
└── frontend/
    ├── package.json
    ├── tsconfig.json
    ├── next.config.js
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── pages/
    │   └── index.tsx
    └── styles/
        └── globals.css
```

## Key decisions

- Mirrors real project tooling: `uv`, `nodemon`, `make`, same ports (8000/3000)
- Same Temporal patterns: `@workflow.defn`, `@activity.defn`, pydantic data converter, task queue
- SQLite auto-inits on `make install` — zero candidate effort
- No LLM, no complex business logic — just the simplest possible workflow
- Brief inline comments explain what workflows and activities are

## README sections

1. Prerequisites — Homebrew, Python 3.12+, Node 18+, Git
2. What is Temporal? — 4-5 sentences on workflows, activities, workers, server
3. Getting Started — brew install, make install
4. Running — 4 terminal commands
5. Verify — visit localhost:3000, click button, see "Hello, World!"
