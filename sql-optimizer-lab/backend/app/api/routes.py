from __future__ import annotations
import asyncio, uuid
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from app.db.connector import ping
from app.db.schema import inspect_schema
from app.models.schemas import AnalyzeRequest, OptimizeJob, ConnectionConfig
from app.engine.optimizer import OptimizerService

router = APIRouter(prefix="/api")
JOBS: dict[str, OptimizeJob] = {}
QUEUES: dict[str, list[asyncio.Queue]] = {}

async def broadcast(job_id: str, event: dict):
    for q in list(QUEUES.get(job_id, [])):
        await q.put(event)

@router.get("/health")
def health(): return {"ok": True}

@router.post("/connections/test")
def test_connection(cfg: ConnectionConfig):
    try: return ping(cfg)
    except Exception as exc: raise HTTPException(status_code=400, detail=str(exc))

@router.post("/connections/schema")
def schema(cfg: ConnectionConfig):
    try:
        return inspect_schema(cfg)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/optimize", response_model=OptimizeJob)
async def start(req: AnalyzeRequest):
    job_id = str(uuid.uuid4())
    job = OptimizeJob(job_id=job_id, status="queued")
    JOBS[job_id] = job
    QUEUES[job_id] = []
    async def emitter(event): await broadcast(job_id, event)
    async def task():
        job.status = "running"
        await emitter({"type":"started", "job_id": job_id})
        await OptimizerService(req, emitter).run(job)
    asyncio.create_task(task())
    return job

@router.post("/jobs/{job_id}/cancel", response_model=OptimizeJob)
async def cancel(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    job = JOBS[job_id]
    if job.status in {"queued", "running"}:
        job.cancel_requested = True
        await broadcast(job_id, {"type": "cancel_requested", "job": job.model_dump()})
    return job

@router.get("/jobs/{job_id}", response_model=OptimizeJob)
def get_job(job_id: str):
    if job_id not in JOBS: raise HTTPException(status_code=404, detail="Job not found")
    return JOBS[job_id]

@router.websocket("/jobs/{job_id}/ws")
async def ws(job_id: str, websocket: WebSocket):
    if job_id not in JOBS:
        await websocket.close(code=4404); return
    await websocket.accept()
    q = asyncio.Queue()
    QUEUES.setdefault(job_id, []).append(q)
    await websocket.send_json({"type":"snapshot","job":JOBS[job_id].model_dump()})
    try:
        while True:
            if JOBS[job_id].status in {"completed","failed"} and q.empty():
                await websocket.send_json({"type":"final","job":JOBS[job_id].model_dump()})
                break
            try:
                event = await asyncio.wait_for(q.get(), timeout=1.0)
                await websocket.send_json(event)
            except asyncio.TimeoutError:
                await websocket.send_json({"type":"heartbeat","status":JOBS[job_id].status,"progress":JOBS[job_id].progress})
    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        if q in QUEUES.get(job_id, []): QUEUES[job_id].remove(q)
