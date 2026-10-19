-- Rule: exists_to_join_advisory
-- Correlated EXISTS subquery that is evaluated per employee.
SELECT
    e.employee_id,
    e.first_name,
    e.last_name
FROM employees e
WHERE EXISTS (
    SELECT 1
    FROM tasks t
    WHERE t.assigned_to = e.employee_id
      AND t.status = 'BLOCKED'
);
