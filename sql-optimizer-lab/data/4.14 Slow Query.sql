-- Rule: implicit_conversion_advisory
-- The numeric columns are compared with quoted string literals.
SELECT
    t.task_id,
    t.task_name
FROM tasks t
WHERE t.assigned_to = '1234'
  AND t.project_id > '4000';
