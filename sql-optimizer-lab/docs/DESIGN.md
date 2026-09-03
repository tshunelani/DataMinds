# Design notes

## Optimization loop

1. Validate one SELECT/CTE/UNION statement.
2. Capture baseline EXPLAIN plus runtime metrics.
3. Generate bounded candidates using SQLGlot transforms and optional LLM suggestions.
4. Use a small epsilon-greedy contextual bandit over transformation operators.
5. Benchmark candidates repeatedly and use median latency for the reward calculation.
6. Promote the fastest completed candidate as the current best.
7. Generate another bounded candidate pass from the best query.
8. Emit every state transition over WebSocket for live UI updates.

## Reward

`reward = 100 * (baseline_ms - candidate_median_ms) / baseline_ms`

This is reinforcement-style rather than deep reinforcement learning. The learner is intentionally simple and transparent so that experiment results can be inspected and reproduced. It can later be replaced by Thompson sampling, LinUCB, a learned ranking model, or an offline policy trained from job history.

## Extending the engine

Add new transformations under `backend/app/engine/rewrites.py`, return a stable `operator` name, and the learning policy will automatically accumulate reward statistics for it.
