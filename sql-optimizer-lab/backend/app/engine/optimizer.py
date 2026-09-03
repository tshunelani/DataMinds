from __future__ import annotations
import asyncio, hashlib, uuid
from collections import defaultdict
from app.engine.executor import DBExecutor
from app.engine.learning import ReinforcementLearner
from app.engine.rewrites import generate_rule_candidates
from app.engine.safety import validate_read_only
from app.models.schemas import AnalyzeRequest, IterationRecord, OptimizeJob

try:
    from app.engine.llm import generate_llm_candidates
except Exception:
    generate_llm_candidates = None

class OptimizerService:
    def __init__(self, request: AnalyzeRequest, emit):
        self.request = request
        self.emit = emit
        self.learner = ReinforcementLearner()

    async def run(self, job: OptimizeJob):
        req = self.request
        executor = None
        try:
            validate_read_only(req.sql)
            executor = DBExecutor(req.connection, req.timeout_ms)
            if job.cancel_requested:
                job.status = "cancelled"
                await self.emit({"type": "completed", "job": job.model_dump()})
                return
            await self.emit({"type": "stage", "stage": "baseline", "message": "Running baseline benchmark"})
            baseline_metric, baseline_plan, _ = await asyncio.to_thread(executor.explain_and_run, req.sql)
            baseline = IterationRecord(iteration=0, candidate_id="baseline", operator="baseline", sql=req.sql, status="completed", metric=baseline_metric, plan_summary=baseline_plan, explanation="Original query baseline")
            job.baseline = baseline
            job.best = baseline
            job.progress = 10
            await self.emit({"type": "baseline", "record": baseline.model_dump()})

            current_sql = req.sql
            seen = {self._fingerprint(req.sql)}
            all_rewrites = generate_rule_candidates(req.sql, req.connection.db_type)
            if req.use_llm and generate_llm_candidates:
                all_rewrites.extend(await generate_llm_candidates(req.sql, req.connection.db_type))
            job.optimization_advisories = list(dict.fromkeys(r.rationale for r in all_rewrites if not r.executable))[:12]
            # bounded pool
            pool = []
            for r in all_rewrites:
                if not r.executable:
                    continue
                fp = self._fingerprint(r.sql)
                if fp not in seen:
                        if r.executable:
                            seen.add(fp); pool.append(r)
            pool = pool[:20]

            history = []
            for i in range(1, req.iterations + 1):
                if job.cancel_requested:
                    job.status = "cancelled"
                    await self.emit({"type": "completed", "job": job.model_dump()})
                    return
                await self.emit({"type": "stage", "stage": "iteration", "iteration": i, "message": f"Selecting candidate for iteration {i}"})
                if not pool:
                    break
                operators = [r.operator for r in pool]
                chosen_op = self.learner.choose(operators)
                idx = next(j for j,r in enumerate(pool) if r.operator == chosen_op)
                rewrite = pool.pop(idx)
                rec = await self._evaluate(executor, rewrite, i, job.best.metric.elapsed_ms if job.best and job.best.metric else baseline_metric.elapsed_ms)
                job.iterations.append(rec)
                history.append(rec)
                reward = rec.reward or -100.0
                self.learner.update(rec.operator, reward)
                if rec.status == "completed" and rec.metric and job.best and job.best.metric and rec.metric.elapsed_ms < job.best.metric.elapsed_ms:
                    job.best = rec
                    current_sql = rec.sql
                job.progress = min(95, 10 + int(85 * i / req.iterations))
                await self.emit({"type": "iteration", "record": rec.model_dump(), "progress": job.progress, "learning": self.learner.snapshot()})

                # generate one more pass from the best candidate if available
                if job.best and i < req.iterations:
                    more = generate_rule_candidates(job.best.sql, req.connection.db_type)
                    for r in more:
                        fp = self._fingerprint(r.sql)
                        if fp not in seen:
                            seen.add(fp); pool.append(r)
                    pool = pool[:20]

            job.index_recommendations = self._index_recommendations(history, req.sql)
            job.learning = self.learner.snapshot()
            job.progress = 100
            job.status = "completed"
            await self.emit({"type": "completed", "job": job.model_dump()})
        except Exception as exc:
            job.status = "failed"
            job.error = str(exc)
            await self.emit({"type": "error", "error": str(exc), "job": job.model_dump()})
        finally:
            if executor is not None:
                executor.close()

    async def _evaluate(self, executor, rewrite, iteration, baseline_ms):
        try:
            # Median-style winner: average repeated runs, preserving the user's requested repeat count.
            times = []
            plan = {}
            metric = None
            for _ in range(self.request.repeats):
                metric, plan, _ = await asyncio.to_thread(executor.explain_and_run, rewrite.sql)
                times.append(metric.elapsed_ms)
            times.sort()
            median_ms = times[len(times)//2]
            metric.elapsed_ms = median_ms
            improvement = (baseline_ms - median_ms) / max(baseline_ms, 0.001)
            reward = improvement * 100.0
            status = "completed"
            return IterationRecord(iteration=iteration, candidate_id=str(uuid.uuid4()), operator=rewrite.operator, sql=rewrite.sql, status=status, metric=metric, reward=reward, plan_summary=plan, explanation=rewrite.rationale)
        except Exception as exc:
            return IterationRecord(iteration=iteration, candidate_id=str(uuid.uuid4()), operator=rewrite.operator, sql=rewrite.sql, status="failed", reward=-100, error=str(exc), explanation=rewrite.rationale)

    def _index_recommendations(self, records, original_sql):
        recs = []
        for r in records:
            plan = r.plan_summary or {}
            if plan.get("seq_scans", 0) > 0:
                recs.append("Inspect WHERE/JOIN columns used by the sequential scan; consider a composite index matching the most selective equality predicate followed by range/order columns.")
            if plan.get("sort_nodes", 0) > 0:
                recs.append("Inspect ORDER BY/GROUP BY columns; a matching index can reduce explicit sort work when the query shape permits ordered index access.")
            if plan.get("disk_reads", 0) and plan.get("disk_reads", 0) > 1000:
                recs.append("High shared disk reads detected; review selective indexes, table bloat/statistics, and whether the query filters early enough.")
        return list(dict.fromkeys(recs))[:5]

    @staticmethod
    def _fingerprint(sql: str) -> str:
        return hashlib.sha1(" ".join(sql.lower().split()).encode()).hexdigest()
