-- Rule: lateral_join_advisory
-- LATERAL subquery re-runs once per employee (10,000 times) against 500,000 tasks.
SELECT
    e.employee_id,
    e.first_name,
    latest.task_name,
    latest.due_date
FROM employees e
JOIN LATERAL (
    SELECT t.task_name, t.due_date
    FROM tasks t
    WHERE t.assigned_to = e.employee_id
    ORDER BY t.due_date DESC
    LIMIT 1
) latest ON TRUE;
