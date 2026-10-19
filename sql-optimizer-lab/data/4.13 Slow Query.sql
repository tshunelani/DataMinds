-- Rule: prefix_like_index_advisory
-- Trailing-only wildcard can use an index (text_pattern_ops or C collation) once one exists.
SELECT
    t.task_id,
    t.task_name
FROM tasks t
WHERE t.task_name LIKE 'Task 4999%';
