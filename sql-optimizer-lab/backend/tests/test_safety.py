import asyncio
import pytest
from app.engine.safety import validate_read_only
from app.engine.rewrites import generate_rule_candidates
from app.engine.optimizer import OptimizerService
from app.models.schemas import AnalyzeRequest, ConnectionConfig, OptimizeJob

def test_select_allowed(): validate_read_only("SELECT 1")
def test_write_blocked():
    with pytest.raises(ValueError): validate_read_only("DELETE FROM users")

def test_distinct_candidate_is_generated():
    candidates = generate_rule_candidates("SELECT DISTINCT id FROM users", "sqlite")
    assert any(candidate.operator == "remove_distinct" for candidate in candidates)

def test_invalid_query_fails_job():
    request = AnalyzeRequest(connection=ConnectionConfig(db_type="sqlite", database=":memory:"), sql="SELECT FROM")
    job = OptimizeJob(job_id="test", status="queued")
    events = []

    async def emit(event):
        events.append(event)

    asyncio.run(OptimizerService(request, emit).run(job))

    assert job.status == "failed"
    assert job.error
    assert events[-1]["type"] == "error"
