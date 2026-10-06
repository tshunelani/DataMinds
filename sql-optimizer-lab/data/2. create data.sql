-- ============================================================
-- LOCATIONS
-- 20 rows
-- ============================================================

INSERT INTO locations (
    location_id,
    location_name,
    city,
    country
)
OVERRIDING SYSTEM VALUE
SELECT
    gs,
    'Location ' || gs,
    CASE ((gs - 1) % 10)
        WHEN 0 THEN 'Johannesburg'
        WHEN 1 THEN 'Cape Town'
        WHEN 2 THEN 'Durban'
        WHEN 3 THEN 'Pretoria'
        WHEN 4 THEN 'Gqeberha'
        WHEN 5 THEN 'London'
        WHEN 6 THEN 'New York'
        WHEN 7 THEN 'Sydney'
        WHEN 8 THEN 'Toronto'
        ELSE 'Berlin'
    END,
    CASE
        WHEN gs <= 5 THEN 'South Africa'
        WHEN gs <= 7 THEN 'United Kingdom'
        WHEN gs = 8 THEN 'United States'
        WHEN gs = 9 THEN 'Australia'
        WHEN gs = 10 THEN 'Canada'
        ELSE 'Germany'
    END
FROM generate_series(1, 20) AS gs;


-- ============================================================
-- DEPARTMENTS
-- 200 rows
-- ============================================================

INSERT INTO departments (
    department_id,
    department_name,
    location_id
)
OVERRIDING SYSTEM VALUE
SELECT
    gs,
    'Department ' || gs,
    ((gs - 1) % 20) + 1
FROM generate_series(1, 200) AS gs;


-- ============================================================
-- EMPLOYEES
-- 10,000 rows
-- ============================================================

INSERT INTO employees (
    employee_id,
    first_name,
    last_name,
    email,
    department_id,
    manager_id,
    hire_date,
    salary
)
OVERRIDING SYSTEM VALUE
SELECT
    gs,
    'First' || gs,
    'Last' || gs,
    'employee' || gs || '@company.com',

    -- Department 1-200
    ((gs - 1) % 200) + 1,

    -- First 200 employees are managers
    -- Remaining employees report to one of them
    CASE
        WHEN gs <= 200 THEN NULL
        ELSE ((gs - 1) % 200) + 1
    END,

    -- Hire dates
    DATE '2016-01-01' + ((gs * 17) % 3650),

    -- Positive salaries
    40000 + ((gs * 137) % 100000)

FROM generate_series(1, 10000) AS gs;


-- ============================================================
-- PROJECTS
-- 5,000 rows
-- ============================================================

INSERT INTO projects (
    project_id,
    project_name,
    department_id,
    project_manager,
    start_date,
    end_date,
    budget,
    status
)
OVERRIDING SYSTEM VALUE
SELECT
    gs,
    'Project ' || gs,

    -- Department 1-200
    ((gs - 1) % 200) + 1,

    -- Employee 1-10,000
    ((gs - 1) % 10000) + 1,

    -- Start date
    DATE '2020-01-01' + ((gs * 23) % 2200),

    -- Some projects are still active and therefore have no end date
    CASE
        WHEN gs % 5 = 0 THEN NULL
        ELSE
            DATE '2020-01-01'
            + ((gs * 23) % 2200)
            + ((gs % 365) + 30)
    END,

    -- Positive budget
    50000 + ((gs * 7919) % 4950000),

    -- ONLY values allowed by chk_project_status
    CASE (gs % 4)
        WHEN 0 THEN 'PLANNED'
        WHEN 1 THEN 'ACTIVE'
        WHEN 2 THEN 'COMPLETED'
        ELSE 'CANCELLED'
    END

FROM generate_series(1, 5000) AS gs;


-- ============================================================
-- TASKS
-- 500,000 rows
-- ============================================================

INSERT INTO tasks (
    task_id,
    project_id,
    assigned_to,
    task_name,
    status,
    priority,
    estimated_hours,
    actual_hours,
    due_date
)
OVERRIDING SYSTEM VALUE
SELECT
    gs,

    -- Project 1-5,000
    ((gs - 1) % 5000) + 1,

    -- Employee 1-10,000
    ((gs - 1) % 10000) + 1,

    'Task ' || gs,

    -- Task status
    CASE
        WHEN gs % 100 < 45 THEN 'TODO'
        WHEN gs % 100 < 75 THEN 'IN_PROGRESS'
        WHEN gs % 100 < 95 THEN 'DONE'
        ELSE 'BLOCKED'
    END,

    -- Task priority
    CASE
        WHEN gs % 100 < 10 THEN 'CRITICAL'
        WHEN gs % 100 < 35 THEN 'HIGH'
        WHEN gs % 100 < 80 THEN 'MEDIUM'
        ELSE 'LOW'
    END,

    -- Estimated hours >= 0
    1 + ((gs * 13) % 80),

    -- Actual hours >= 0 or NULL
    CASE
        WHEN gs % 10 = 0 THEN NULL
        ELSE 1 + ((gs * 17) % 100)
    END,

    -- Due date
    DATE '2025-01-01' + ((gs * 7) % 1000)

FROM generate_series(1, 500000) AS gs;


-- ============================================================
-- RESET IDENTITY SEQUENCES
-- ============================================================

SELECT setval(
    pg_get_serial_sequence('locations', 'location_id'),
    (SELECT MAX(location_id) FROM locations)
);

SELECT setval(
    pg_get_serial_sequence('departments', 'department_id'),
    (SELECT MAX(department_id) FROM departments)
);

SELECT setval(
    pg_get_serial_sequence('employees', 'employee_id'),
    (SELECT MAX(employee_id) FROM employees)
);

SELECT setval(
    pg_get_serial_sequence('projects', 'project_id'),
    (SELECT MAX(project_id) FROM projects)
);

SELECT setval(
    pg_get_serial_sequence('tasks', 'task_id'),
    (SELECT MAX(task_id) FROM tasks)
);


-- ============================================================
-- UPDATE STATISTICS
-- ============================================================

ANALYZE locations;
ANALYZE departments;
ANALYZE employees;
ANALYZE projects;
ANALYZE tasks;