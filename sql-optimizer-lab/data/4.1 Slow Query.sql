SELECT
    l.location_name,
    d.department_name,
    e.first_name || ' ' || e.last_name AS employee,
    p.project_name,
    t.task_name,
    t.status,
    t.priority
FROM locations l
JOIN departments d
    ON d.location_id = l.location_id
JOIN employees e
    ON e.department_id = d.department_id
JOIN tasks t
    ON t.assigned_to = e.employee_id
JOIN projects p
    ON p.project_id = t.project_id
ORDER BY
    l.location_name,
    d.department_name,
    employee,
    p.project_name,
    t.task_name;