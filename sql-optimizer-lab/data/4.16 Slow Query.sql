-- Rule: union_all_advisory
-- UNION pays for duplicate elimination. The two branches can never overlap (different statuses),
-- so UNION ALL returns the same rows without the sort/hash step.
SELECT t.task_id, t.task_name, t.status
FROM tasks t
WHERE t.status = 'BLOCKED'
UNION
SELECT t.task_id, t.task_name, t.status
FROM tasks t
WHERE t.status = 'DONE';
