-- Rule: in_to_exists_advisory
-- IN over a large subquery (500,000 tasks) where EXISTS can stop at the first match.
SELECT
    e.employee_id,
    e.first_name,
    e.last_name
FROM employees e
WHERE e.employee_id IN (
    SELECT t.assigned_to
    FROM tasks t
    WHERE t.priority = 'CRITICAL'
);
