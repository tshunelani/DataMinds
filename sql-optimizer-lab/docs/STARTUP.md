# Startup Guide

## Prerequisites

- Python 3.10 or newer
- Node.js 22 or newer
- PostgreSQL installed and running only when connecting to a local PostgreSQL database

Run the backend and frontend in separate Git Bash terminals. All commands below assume the repository root is `sql-optimizer-lab`.

## Backend

```bash
cd backend

# Create and activate the virtual environment (first run only).
python -m venv .venv
. .venv/Scripts/activate

# Confirm that Python is being loaded from .venv.
which python

# Install dependencies and create local configuration (first run only).
pip install -r requirements.txt
cp .env.example .env

# Create the SQLite demo database (optional, first run only).
python -m app.seed_demo

# Start FastAPI.
python -m uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs to verify that the API is running.

`python -m uvicorn` ensures Git Bash uses the Uvicorn installed in the activated virtual environment. Use it if `uvicorn app.main:app --port 8000` exits with code `126`.

## Frontend

In a second Git Bash terminal:

```bash
cd frontend

# Install dependencies and create local configuration (first run only).
npm install
cp .env.local.example .env.local

# Start Next.js.
npm run dev
```

Open http://localhost:3000.

## Connect To Local PostgreSQL

Docker is optional. A PostgreSQL service installed on this computer can be used directly.

1. Start PostgreSQL using its Windows service, pgAdmin, or another local PostgreSQL tool.
2. Start the backend and frontend using the commands above.
3. In the application, set **Engine** to `PostgreSQL` and enter:

| Field | Typical local value |
| --- | --- |
| Database / path | Your database name, for example `optimizer_demo` |
| Host | `localhost` |
| Port | `5432` |
| User | Your PostgreSQL login, for example `postgres` |
| Password | The password for that login |
| SSL mode | Leave empty for a typical local installation |

4. Select **Test connection**. `Connection OK` confirms that the FastAPI backend can reach PostgreSQL. The database user should have read-only access to the schemas and tables you plan to analyze.

## Docker Database Helpers

The compose file is in the repository root, so run Docker from `sql-optimizer-lab`, not its parent `sql optimizer` directory:

```bash
cd "/c/Users/tshunelanim/OneDrive - MIP Holdings (Pty) Ltd/Desktop/Work/sql optimizer/sql-optimizer-lab"
docker compose up -d postgres mysql
```

This starts separate Docker-managed PostgreSQL and MySQL demo services. It is not required for a locally installed PostgreSQL server. Docker PostgreSQL uses `localhost:5432`, database `optimizer_demo`, user `optimizer`, and password `optimizer`.

If local PostgreSQL already uses port `5432`, do not start the Docker PostgreSQL service unless you change one of the port mappings in `docker-compose.yml`.

