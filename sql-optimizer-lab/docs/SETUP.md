# Local installation

## Prerequisites

- Python 3.12 recommended (FastAPI currently requires Python >=3.10).
- Node.js 22 recommended.
- For PostgreSQL/MySQL, a reachable DB account with read-only privileges.
- For SQL Server, Microsoft ODBC Driver 18 for SQL Server installed on the machine running the FastAPI backend.

## Windows

```powershell
cd sql-optimizer-lab\backend
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.seed_demo
uvicorn app.main:app --reload --port 8000
```

Open another PowerShell window:

```powershell
cd sql-optimizer-lab\frontend
copy .env.local.example .env.local
npm install
npm run dev
```

Open http://localhost:3000.

## Linux/macOS

```bash
cd sql-optimizer-lab/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.seed_demo
uvicorn app.main:app --reload --port 8000
```

Then:

```bash
cd ../frontend
cp .env.local.example .env.local
npm install
npm run dev
```

## Docker helpers

```bash
docker compose up -d postgres mysql
```

The app itself can be containerized with the supplied Dockerfiles, but the default developer workflow uses the local Python/Node processes so database driver installation is easier to troubleshoot.
