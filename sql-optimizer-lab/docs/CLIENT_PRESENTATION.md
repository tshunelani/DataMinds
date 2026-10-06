# SQL Optimization Workbench

## Client Demonstration Presentation

**Target duration:** 10-15 minutes  
**Audience:** Engineering leaders, database administrators, data platform teams, and application owners

---

## Slide 1: Turn Slow Queries Into Measurable Improvements

**On slide**

- SQL Optimization Workbench
- Find, test, and explain safer query improvements
- From a slow query to evidence-backed next steps

**Speaker notes, 45 seconds**

Most teams know which queries are slow, but the difficult part is deciding what to change and proving that the change actually helps. The SQL Optimization Workbench gives teams a repeatable way to start with a read-only query, establish a baseline, test alternative forms, and see the best observed result.

Today I will show the complete workflow using a deliberately inefficient query, from connection and schema inspection through optimization results and recommendations.

---

## Slide 2: The Problem We Address

**On slide**

- Slow queries affect user experience and infrastructure cost
- Manual tuning depends heavily on specialist time
- A rewrite that looks better is not always faster in practice
- Teams need evidence, not just suggestions

**Speaker notes, 60 seconds**

Query tuning often involves several disconnected activities: finding the query, reading the execution plan, trying a rewrite, running it, and documenting the result. That process is slow and difficult to standardize.

The workbench brings those steps together. It does not simply produce a prettier SQL statement. It compares the original query with bounded alternatives and measures the candidates against the connected database.

The important distinction is that the result is performance evidence: baseline latency, candidate latency, execution-plan information, and the reason a recommendation was raised.

---

## Slide 3: What the Workbench Does

**On slide**

1. Connects to a supported database or demo dataset
2. Inspects schema and indexes
3. Validates that the query is read-only
4. Captures a baseline plan and runtime
5. Generates rule-based and optional AI-assisted candidates
6. Repeats candidate execution and selects the best observed result
7. Explains the change and recommends follow-up actions

**Speaker notes, 60 seconds**

The workflow is deliberately bounded. The application evaluates a single read-only query at a time. It can work with SQLite, PostgreSQL, MySQL, and SQL Server connection configurations, with the richest plan information currently available for PostgreSQL.

The workbench does not silently modify a database. It measures the query and provides SQL and recommendations for an engineer to review.

---

## Slide 4: A Safe Starting Point

**On slide**

- Read-only query validation
- Single-statement enforcement
- Configurable execution timeout
- Repeated runs with median-style comparison
- Cancellation support for the optimization job

**Speaker notes, 60 seconds**

Safety is part of the workflow, not an afterthought. Before optimization, the query is checked to ensure it is a permitted read-only statement such as a `SELECT`, CTE, or `UNION`.

Each candidate is evaluated within configured limits. Repeating executions helps reduce the effect of one noisy timing result, while the timeout protects the database from an unexpectedly expensive candidate.

For a production rollout, we would pair this with the client’s access controls, workload policies, and approval process.

---

## Slide 5: Live Demo Setup

**On slide**

- Connection: Demo SQLite
- Query: order and customer aggregation
- Settings: 4 iterations, 3 runs per candidate, 5-second timeout
- Optional LLM candidates: off for the first pass

**Speaker notes, 45 seconds**

I will use the built-in demo connection so the workflow is reproducible without touching a client production database. The query is designed to expose a common tuning opportunity: applying a function to a date column in a filter, which can make index use more difficult.

The settings are intentionally modest. In a real environment, the number of iterations and runs would be chosen based on query cost and the acceptable evaluation window.

---

## Slide 6: Step 1 - Connect and Understand the Data

**On screen during demo**

1. Select **Demo SQLite**.
2. Click **Test connection**.
3. Click **Load schema**.
4. Point out tables, columns, and indexes.

**Speaker notes, 60 seconds**

Before changing SQL, the user can confirm connectivity and load a schema snapshot. This gives immediate context: what tables exist, which columns are available, and where indexes may already support the workload.

This is useful for two reasons. It reduces the chance of tuning against an incorrect assumption, and it gives the recommendation engine the database objects it needs when it reports possible indexing or access-path improvements.

---

## Slide 7: Step 2 - Establish a Baseline

**On screen during demo**

1. Review the query in the editor.
2. Click **Optimize query**.
3. Show the baseline status and first execution measurement.

**Speaker notes, 75 seconds**

The first measurement is our control. The workbench captures the original query’s execution time and plan information before promoting any alternative.

The live progress view shows that the system is working through a sequence rather than returning an unexplained answer. That transparency matters when a result will inform a code review, a DBA decision, or a capacity discussion.

The baseline gives us the number against which every candidate is judged. Without it, an optimization percentage is only a claim.

---

## Slide 8: Step 3 - Test Explainable Alternatives

**On screen during demo**

- Candidate SQL rewrites
- Iteration progress
- Execution time per candidate
- Reward and learning-policy statistics
- Plan cost, rows, and disk-read signals where available

**Speaker notes, 90 seconds**

The engine generates bounded candidates from known optimization patterns. Examples include replacing equality chains with `IN`, making date predicates more index-friendly, and flagging conditions that may prevent an index from being used effectively.

Each candidate is executed repeatedly, and the workbench records the observed result. The lightweight learning policy helps balance trying alternatives with spending more evaluation effort on promising candidates. This is a practical search strategy for the current job, not a claim of autonomous deep learning.

Where the database exposes the information, the workbench also uses plan cost, row counts, sequential scans, sorts, and disk reads to support the timing result.

---

## Slide 9: Step 4 - Read the Result

**On slide**

- Baseline execution time
- Best observed execution time
- Improvement percentage
- Performance history chart
- Original versus optimized SQL

**Speaker notes, 90 seconds**

This is the decision point. The workbench promotes the fastest successful candidate as the current best and shows the improvement against the baseline.

The chart helps us see whether the result is stable or whether one run was an outlier. The SQL comparison makes the proposed change reviewable. An engineer can copy the optimized SQL, inspect it, and decide whether it belongs in the application or reporting workload.

The goal is not to hide the reasoning behind a score. The goal is to make the proposed change easy to inspect and easy to challenge.

---

## Slide 10: From Query Change to Engineering Action

**On slide**

- Index recommendations
- Optimization checks and advisories
- SARGability warnings
- Sequential scan and sort signals
- `LIKE`, `JOIN`, `HAVING`, and `UNION ALL` guidance

**Speaker notes, 75 seconds**

Sometimes the best answer is not a rewrite. The workbench can surface an index recommendation or an advisory about a predicate, join, sort, or aggregation.

These outputs turn the demo into an action list. The team can take the optimized SQL into a code review, validate an index in a staging environment, or investigate a broader data-model issue.

The workbench recommends; it does not create indexes or change schema automatically. That keeps the final engineering decision with the people who understand the workload and its operational constraints.

---

## Slide 11: Optional AI Assistance, With Human Review

**On slide**

- Optional OpenAI-generated candidates
- Rule-based candidates remain available
- Candidates are measured against the baseline
- Engineers review the final SQL before adoption

**Speaker notes, 60 seconds**

For teams that want broader exploration, the workbench can request additional candidate rewrites from an OpenAI model. This is optional; the rules-based workflow works without it.

The useful role for AI here is idea generation. The useful role for the database is measurement. The useful role for the engineer is approval. That separation keeps an attractive suggestion from being treated as a production change without review.

For a production deployment, AI-generated SQL should be subject to the same validation, security controls, and semantic-equivalence checks as every other candidate.

---

## Slide 12: Why This Matters to a Client

**On slide**

- Shorter path from slow query to tested hypothesis
- Repeatable tuning workflow across teams
- Evidence for engineering and capacity decisions
- Explainable recommendations instead of opaque automation
- No automatic schema changes

**Speaker notes, 60 seconds**

The immediate value is faster investigation. The broader value is consistency: teams can use the same workflow to measure a baseline, compare alternatives, and capture the reasoning behind a recommendation.

That can support application performance work, database reviews, release validation, and targeted cost reduction. It also creates a useful boundary for adoption: the workbench accelerates analysis and recommendation, while existing deployment and change-management controls remain in place.

---

## Slide 13: Practical Adoption Path

**On slide**

**Phase 1: Guided evaluation**

- Use representative read-only queries
- Compare results in a non-production environment
- Confirm timing and plan behavior with DBAs

**Phase 2: Team workflow**

- Add query review to performance investigations
- Capture approved rewrites and index decisions
- Establish workload-specific safety limits

**Phase 3: Production hardening**

- Add authentication and durable job history
- Add semantic result comparison
- Strengthen candidate validation and audit controls

**Speaker notes, 60 seconds**

The sensible path is incremental. Start with representative queries in a controlled environment and validate the measurements with the client’s database specialists.

As usage grows, hardening priorities include authentication, durable history, multi-user isolation, stronger equivalence checks, and a full audit trail. Those capabilities matter when the workbench becomes part of an operational performance process rather than a guided lab.

---

## Slide 14: Closing - A Better Tuning Conversation

**On slide**

- What is slow?
- What can we change?
- Did it actually improve?
- What evidence supports the decision?

**Speaker notes, 45 seconds**

The workbench gives teams a concrete way to answer those four questions. It starts with the query they already have, measures the current behavior, evaluates alternatives, and presents the result in a form an engineer can review.

The outcome is not just faster SQL. It is a more disciplined and explainable tuning conversation.

**Suggested close:**

“For a next step, we can take a small set of representative slow queries, run them in a controlled environment, and identify where measured rewrites or indexing recommendations could have the greatest impact.”

---

## Live Demo Checklist

- Start the backend and frontend before the meeting.
- Open the workbench at the local frontend URL.
- Confirm the **Demo SQLite** connection is available.
- Test the connection and load the schema before presenting.
- Keep the first run at 4 iterations, 3 runs per candidate, and a 5,000 ms timeout.
- Have one read-only fallback query ready in case the seeded demo data is unavailable.
- Explain that exact timings vary by machine and data distribution.
- Use the result screen to show baseline, best result, improvement, chart, advisories, and SQL diff.
- Treat LLM candidates as an optional second pass, not a requirement for the core demonstration.

## Claims to Keep Precise

- Say **“best observed execution time”**, not “guaranteed performance.”
- Say **“candidate rewrite”**, not “automatically safe production SQL.”
- Say **“recommendation”**, not “automatic index creation.”
- Say **“lightweight learning policy”**, not “deep-learning optimizer.”
- Say **“read-only optimization workflow”**, not “full production query governance platform.”
