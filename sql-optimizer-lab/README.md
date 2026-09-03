# SQL Optimizer Lab

A local full-stack application that benchmarks a read-only SQL query, generates rule/LLM-assisted candidates, analyzes execution plans, iterates with reinforcement-style rewards, and returns the fastest semantically valid candidate.

## Architecture

- Frontend: Next.js 16.3.3, React 19, TypeScript, Tailwind CSS, Monaco Editor, Recharts, Lucide.
- Backend: FastAPI, SQLAlchemy, SQLGlot, Pydantic Settings.
- Databases: SQLite, PostgreSQL, MySQL, Microsoft SQL Server via SQLAlchemy dialects.
- Learning loop: contextual bandit / epsilon-greedy operator selection backed by in-memory observations.
- Safety: SELECT-only validation, read-only intent, statement timeouts where supported, bounded iterations, no DDL/DML execution.

> This project is an optimization research/engineering tool, not a guarantee that a rewritten query is semantically identical. Always validate optimized SQL against representative data and production-like workloads before deployment.

## Quick start

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.seed_demo
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open http://localhost:3000.

### 3. Demo database

The seed command creates `data/demo.db` with `customers`, `orders`, and `order_items`, plus indexes and sample data. Use the connection panel with:

- Driver: `sqlite`
- Database: `../data/demo.db`

Example query:

```sql
SELECT c.id, c.name, COUNT(o.id) AS order_count
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE date(o.created_at) >= date('now', '-90 day')
  AND c.status = 'active'
GROUP BY c.id, c.name
ORDER BY order_count DESC;
```

## Optional LLM rewriting

Set these variables in `backend/.env`:

```dotenv
LLM_PROVIDER=openai
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5-mini
```

The engine remains fully functional without an LLM; rule-based SQLGlot rewrites are always available.

## Production hardening checklist

1. Store connection credentials in a secrets manager, not the browser or database rows.
2. Run the backend in a network segment that can reach target databases but cannot be used as a general-purpose pivot host.
3. Use a dedicated read-only DB account with least privilege.
4. Enforce allowlists for destination hosts and ports.
5. Use per-connection TLS verification and database-specific statement timeouts.
6. Replace the in-memory job store with Redis + a durable job table for multi-instance deployments.
7. Add authentication/authorization before exposing this service beyond localhost.
8. Add result-set equivalence validation and query-result checksums before accepting an optimization.


### Improvements
When a query is invalid or the database throws an error, the applicattion must stop processing and show the error on screen.

We must have a button to stop the optimizer should it run longer than expect, in this case it should terminate the optimization in the background and return to the screen

### Optimization

Check the impact of a cross join compared to a normal inner join or lateral joins versus left joins 

Select fields explicitly: Replace SELECT * with specific column names to reduce I/O and network payload.

Index frequently queried columns: Place composite B-Tree 

Use EXISTS instead of IN for subqueries: EXISTS short-circuits as soon as a match is found, whereas IN evaluates the entire subquery dataset.

Filter early with WHERE: Filter rows before grouping with WHERE instead of filtering aggregated results with HAVING.
Optimize LIKE wildcards: Avoid leading wildcards (LIKE '%term'), which force a full table scan. Trailing wildcards (LIKE 'term%') can utilize indexes.

Avoid implicit type conversions: Ensure query parameters match column data types (e.g., comparing a string variable to an integer column) to prevent forced implicit functions that bypass indexes.

