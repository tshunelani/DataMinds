-- Rule: leading_like_wildcard_advisory
-- A leading % wildcard prevents index seeks and forces a scan of all employees.
SELECT
    e.employee_id,
    e.email
FROM employees e
WHERE e.email LIKE '%1234@company.com';
