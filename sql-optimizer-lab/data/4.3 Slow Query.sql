-- Rule: remove_distinct
-- employee_id is the primary key, so DISTINCT adds a needless sort/hash step.
SELECT DISTINCT
    e.employee_id,
    e.first_name,
    e.last_name,
    d.department_name
FROM employees e
JOIN departments d
    ON d.department_id = e.department_id
ORDER BY e.employee_id;
