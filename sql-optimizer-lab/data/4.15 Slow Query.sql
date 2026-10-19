-- Rule: sargability_advisory
-- Functions wrapped around columns stop a plain index on those columns from being used.
SELECT
    e.employee_id,
    e.email
FROM employees e
WHERE LOWER(e.email) = 'employee1234@company.com'
   OR UPPER(e.last_name) = 'LAST1234';
