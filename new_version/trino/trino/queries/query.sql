WITH filter_list(val) AS (
    VALUES
    ('value 1'),
    ('value 2'),
)
SELECT t.*
FROM iceberg.my_namespace.my_table as t
INNER JOIN filter_list f ON t.fieldA = f.val
UNION ALL
SELECT t.*
FROM iceberg.my_namespace.my_table as t
INNER JOIN filter_list f ON t.fieldB = f.val