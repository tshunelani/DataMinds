-- Rule: explicit_projection_advisory
-- SELECT * over the largest table returns every column.
SELECT *
FROM tasks t
JOIN projects p
    ON p.project_id = t.project_id
WHERE t.status = 'IN_PROGRESS';
