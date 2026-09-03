# API surface

- `GET /api/health` — health check.
- `POST /api/connections/test` — validates a database connection.
- `POST /api/optimize` — starts an optimization job and returns its job ID.
- `GET /api/jobs/{job_id}` — gets the current job snapshot.
- `WS /api/jobs/{job_id}/ws` — streams baseline, iteration, learning, and completion events.

The request body for `/api/optimize` is:

```json
{
  "connection": {
    "name": "Demo",
    "db_type": "sqlite",
    "database": "../data/demo.db"
  },
  "sql": "SELECT 1",
  "iterations": 4,
  "repeats": 3,
  "timeout_ms": 5000,
  "use_llm": false
}
```
