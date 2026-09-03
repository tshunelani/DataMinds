from __future__ import annotations
import re, time
from sqlalchemy import text
from app.db.connector import create_db_engine
from app.engine.plans import parse_postgres_plan, parse_generic_explain
from app.models.schemas import ConnectionConfig, Metric

class DBExecutor:
    def __init__(self, cfg: ConnectionConfig, timeout_ms: int):
        self.cfg = cfg
        self.timeout_ms = timeout_ms
        self.engine = create_db_engine(cfg)

    def close(self):
        self.engine.dispose()

    def _timeout(self, conn):
        seconds = max(1, int(self.timeout_ms / 1000))
        if self.cfg.db_type == "postgresql":
            conn.execute(text(f"SET LOCAL statement_timeout = {self.timeout_ms}"))
        elif self.cfg.db_type == "mysql":
            # MAX_EXECUTION_TIME applies to SELECT statements in MySQL and is ignored by other statement types.
            conn.execute(text(f"SET SESSION MAX_EXECUTION_TIME={self.timeout_ms}"))
        elif self.cfg.db_type == "mssql":
            # pyodbc execution timeout is not uniformly exposed by SQLAlchemy; this sets a server-side lock/query timeout where available.
            try:
                raw = conn.connection.driver_connection
                raw.timeout = seconds
            except Exception:
                pass

    def explain_and_run(self, sql: str) -> tuple[Metric, dict, str]:
        with self.engine.connect() as conn:
            trans = conn.begin()
            try:
                self._timeout(conn)
                plan_raw = self._explain(conn, sql)
                plan = parse_postgres_plan(plan_raw) if self.cfg.db_type == "postgresql" else parse_generic_explain(plan_raw)
                start = time.perf_counter()
                result = conn.execute(text(sql))
                rows = result.rowcount if result.rowcount >= 0 else None
                # Do not stream arbitrary data to the API. Fetch at most one row solely to force execution in some DBs.
                try: result.fetchmany(1)
                except Exception: pass
                elapsed = (time.perf_counter() - start) * 1000
                metric = Metric(
                    elapsed_ms=elapsed,
                    cache_hits=plan.get("cache_hits"),
                    disk_reads=plan.get("disk_reads"),
                    rows=rows if rows is not None else plan.get("actual_rows"),
                    plan_cost=plan.get("total_cost"),
                    scan_rows=plan.get("actual_rows"),
                )
                return metric, plan, plan_raw
            finally:
                trans.rollback()

    def _explain(self, conn, sql: str) -> str:
        if self.cfg.db_type == "postgresql":
            return str(conn.execute(text("EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + sql)).scalar())
        if self.cfg.db_type == "mysql":
            row = conn.execute(text("EXPLAIN FORMAT=JSON " + sql)).scalar()
            return str(row)
        if self.cfg.db_type == "mssql":
            # SQL Server's plan capture is permission/batch sensitive. Return a conservative text marker
            # and rely on execution metrics unless the deployment enables a dedicated SHOWPLAN pipeline.
            return "SQL Server plan capture requires SHOWPLAN permission and a dedicated batch; execution metrics were collected."
        row = conn.execute(text("EXPLAIN QUERY PLAN " + sql)).fetchall()
        return "\n".join(str(r) for r in row)
