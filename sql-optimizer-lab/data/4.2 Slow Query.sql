-- ALL-IN-ONE demo: triggers every rule except union_all_advisory
-- (UNION ALL advice only fires when the query has no DISTINCT, see 4.16).
-- Rules exercised:
--   remove_distinct, or_to_in, exists_to_join_advisory, in_to_exists_advisory,
--   explicit_projection_advisory, cross_join_advisory, lateral_join_advisory,
--   left_join_advisory, having_filter_advisory, leading_like_wildcard_advisory,
--   prefix_like_index_advisory, implicit_conversion_advisory, sargability_advisory
SELECT DISTINCT
    l.location_name,
    d.department_name,
    e.employee_id,
    e.first_name || ' ' || e.last_name AS employee,
    p.project_name,
    recent.last_due,
    COUNT(t.task_id) AS matching_tasks
FROM locations l
CROSS JOIN (SELECT * FROM departments) d
JOIN employees e
    ON e.department_id = d.department_id
JOIN tasks t
    ON t.assigned_to = e.employee_id
LEFT JOIN projects p
    ON p.project_manager = e.employee_id
LEFT JOIN LATERAL (
    SELECT MAX(t2.due_date) AS last_due
    FROM tasks t2
    WHERE t2.assigned_to = e.employee_id
) recent ON TRUE
WHERE d.location_id = l.location_id
  AND (t.status = 'TODO' OR t.status = 'BLOCKED')
  AND e.email LIKE '%@company.com'
  AND e.last_name LIKE 'Last1%'
  AND e.department_id > '10'
  AND LOWER(e.first_name) <> 'first999'
  AND EXISTS (
        SELECT 1
        FROM projects px
        WHERE px.project_manager = e.employee_id
  )
  AND e.employee_id IN (
        SELECT t3.assigned_to
        FROM tasks t3
        WHERE t3.priority = 'CRITICAL'
  )
GROUP BY
    l.location_name,
    d.department_name,
    e.employee_id,
    e.first_name,
    e.last_name,
    p.project_name,
    recent.last_due
HAVING l.location_name <> 'Location 99'
ORDER BY
    l.location_name,
    d.department_name,
    employee;
