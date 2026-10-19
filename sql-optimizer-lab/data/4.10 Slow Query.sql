-- Rule: left_join_advisory
-- LEFT JOIN where the WHERE clause rejects unmatched rows, so INNER JOIN is equivalent.
SELECT
    e.employee_id,
    e.last_name,
    t.task_name
FROM employees e
LEFT JOIN tasks t
    ON t.assigned_to = e.employee_id
WHERE t.status = 'BLOCKED';
