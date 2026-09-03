from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator

DBType = Literal["sqlite", "postgresql", "mysql", "mssql"]

class ConnectionConfig(BaseModel):
    name: str = "Target DB"
    db_type: DBType
    host: str | None = None
    port: int | None = None
    user: str | None = None
    password: str | None = None
    database: str
    ssl_mode: str | None = None

class AnalyzeRequest(BaseModel):
    connection: ConnectionConfig
    sql: str = Field(min_length=1)
    iterations: int = Field(default=4, ge=1, le=5)
    repeats: int = Field(default=3, ge=1, le=5)
    timeout_ms: int = Field(default=5000, ge=250, le=15000)
    use_llm: bool = False

    @field_validator("sql")
    @classmethod
    def normalize_sql(cls, v: str) -> str:
        return v.strip()

class Candidate(BaseModel):
    id: str
    sql: str
    operator: str
    rationale: str

class Metric(BaseModel):
    elapsed_ms: float
    cpu_ms: float | None = None
    memory_mb: float | None = None
    buffer_reads: int | None = None
    cache_hits: int | None = None
    disk_reads: int | None = None
    rows: int | None = None
    plan_cost: float | None = None
    scan_rows: int | None = None

class IterationRecord(BaseModel):
    iteration: int
    candidate_id: str
    operator: str
    sql: str
    status: str
    metric: Metric | None = None
    reward: float | None = None
    plan_summary: dict[str, Any] = Field(default_factory=dict)
    explanation: str = ""
    error: str | None = None

class OptimizeJob(BaseModel):
    job_id: str
    status: Literal["queued", "running", "completed", "failed", "cancelled"]
    cancel_requested: bool = False
    progress: int = 0
    baseline: IterationRecord | None = None
    iterations: list[IterationRecord] = Field(default_factory=list)
    best: IterationRecord | None = None
    index_recommendations: list[str] = Field(default_factory=list)
    optimization_advisories: list[str] = Field(default_factory=list)
    learning: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
