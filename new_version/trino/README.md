# Apache Iceberg Demo

## Run Iceberg stack
```
docker compose up -d
```

## Setup Bucket in MinIO
If using the minio-client, it's already done. Otherwise, make the `warehouse` bucket in the MinIO UI

## Setup Polaris Catalog
```
python3 polaris-setup.py
```
This creates a user and a catalog. Copy the client id and client secret printed form this into the all spark scritps you run (Replace at the top of the script)

## Run PySpark
Open a Pyspark shell to ingest some sample Parquet.
```
pyspark \
  --master local[50] \
  --driver-memory 1G \
  --num-executors 4 \
  --executor-memory 1G \
  --executor-cores 4 \
  --conf "spark.driver.maxResultSize=5G" \
  --conf "spark.executor.memoryOverhead=5G" \
  --conf "spark.driver.memoryOverhead=5G" \
  --conf "spark.driver.memory=5G" \
  --packages org.apache.iceberg:iceberg-aws-bundle:1.7.0,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.7.0
```

### Ingest Data
Copy the text in `spark-queries/ingest.py` into the shell.

### Z-order the Data
Copy the text in `spark-queries/rewrite.py` into the shell.

### Spark Query
Copy the text in `spark-queries/query.py` into the shell.

## Trino Query
First start the Trino container
```
cd trino
docker compose up -d
```

Run the following command to open a trino shell.
```
docker exec -it trino trino --catalog iceberg --schema my_namespace --pager=""
```

Copy the query in `trino/queries/query.sql` to query the iceberg data.

If polaris loses track of the data in MinIO for any reason, you can register the table using the query in `trino/queries/register.sql`