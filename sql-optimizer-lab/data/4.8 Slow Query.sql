-- Rule: cross_join_advisory
-- CROSS JOIN builds a Cartesian product (20 x 200 rows) that is then filtered.
SELECT
    l.location_name,
    d.department_name
FROM locations l
CROSS JOIN departments d
WHERE d.location_id = l.location_id;
