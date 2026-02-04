CREATE SCHEMA IF NOT EXISTS iceberg.my_namespace

CALL iceberg.system.register_table(
    schema_name => 'my_namespace',
    table_name => 'my_table',
    table_location => 's3://warehouse/my_namespace/my_table'
)