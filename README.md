# Apache Iceberg Demo
Based on https://github.com/AlexMercedCoder/Apache-Polaris-Apache-Iceberg-Minio-Spark-Quickstart

## Environment Setup
### Run Docker Containers
```
docker compose up -d
```
Run `docker ps` and confirm Polaris is healthy before continuing

### Run Polaris Setup script
```
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python polaris-setup.py
```
Then update `CLIENT_ID` and `CLIENT_SECRET` in `ingest.py`

### Run local PySpark
```
pyspark \
  --master local[*] \
  --driver-memory 1G \
  --num-executors 4 \
  --executor-memory 1G \
  --executor-cores 4 \
  --conf "spark.driver.maxResultSize=5G" \
  --conf "spark.executor.memoryOverhead=5G" \
  --conf "spark.driver.memoryOverhead=5G" \
  --conf "spark.driver.memory=5G" \
  --packages org.apache.iceberg:iceberg-aws-bundle:1.10.0,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.0,org.apache.polaris:polaris-spark-3.5_2.12:1.1.0-incubating
```
And copy the text in `ingest.py` in the shell


Spark Version: `3.5.0`
Spark Scala Version: `2.12.18`

MinIO Version: `RELEASE.2025-09-07T16-13-09Z`
Apache Polaris Version: `1.1.0-incubating`

Iceberg jar versions: `1.10.0`