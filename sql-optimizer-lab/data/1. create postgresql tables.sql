CREATE TABLE locations (
    location_id INTEGER PRIMARY KEY,
    location_name VARCHAR(255)
);

CREATE TABLE departments (
    department_id INTEGER PRIMARY KEY,
    department_name VARCHAR(255),
    location_id INTEGER,

    CONSTRAINT fk_department_location
        FOREIGN KEY (location_id)
        REFERENCES locations(location_id)
);

CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    department_id INTEGER,
    manager_id INTEGER,

    CONSTRAINT fk_employee_department
        FOREIGN KEY (department_id)
        REFERENCES departments(department_id),

    CONSTRAINT fk_employee_manager
        FOREIGN KEY (manager_id)
        REFERENCES employees(employee_id)
);

CREATE TABLE projects (
    project_id INTEGER PRIMARY KEY,
    project_name VARCHAR(255),
    department_id INTEGER,
    project_manager INTEGER,

    CONSTRAINT fk_project_department
        FOREIGN KEY (department_id)
        REFERENCES departments(department_id),

    CONSTRAINT fk_project_manager
        FOREIGN KEY (project_manager)
        REFERENCES employees(employee_id)
);

CREATE TABLE tasks (
    task_id INTEGER PRIMARY KEY,
    task_name VARCHAR(255),
    status VARCHAR(50),
    priority VARCHAR(50),
    assigned_to INTEGER,
    project_id INTEGER,

    CONSTRAINT fk_task_employee
        FOREIGN KEY (assigned_to)
        REFERENCES employees(employee_id),

    CONSTRAINT fk_task_project
        FOREIGN KEY (project_id)
        REFERENCES projects(project_id)
);