-- Rule: or_to_in
-- Repeated equality predicates on the same column joined with OR.
SELECT
    t.task_id,
    t.task_name,
    t.status
FROM tasks t
WHERE t.status = 'BLOCKED'
   OR t.status = 'TODO';
