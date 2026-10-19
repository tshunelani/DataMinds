-- Rule: having_filter_advisory
-- The status filter is not an aggregate, so it belongs in WHERE and should run before grouping.
SELECT
    t.status,
    t.priority,
    COUNT(t.task_id) AS task_count
FROM tasks t
GROUP BY t.status, t.priority
HAVING t.status = 'BLOCKED';
