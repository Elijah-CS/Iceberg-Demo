from pyspark.sql import SparkSession

POLARIS_BASE_URL = "http://localhost:8181"
MINIO_BASE_URL = "http://localhost:9000"

CATALOG_NAME = "polaris_catalog"
CLIENT_ID = "94f1f5b42affc2d8"
CLIENT_SECRET = "a004634f2f14141c3c00b82a5734895b"

MINIO_USER = "admin"
MINIO_PASS = "password"

if "spark" in locals() or "spark" in globals():
    spark.stop()

spark_packages = [
    "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.7.0",
    "org.apache.iceberg:iceberg-aws-bundle:1.7.0",
]

spark = (SparkSession.builder
    .config(f"spark.jars.packages", ",".join(spark_packages))
    .config(f"spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
    .config(f"spark.sql.{CATALOG_NAME}.polaris", "org.apache.polaris.spark.SparkCatalog")
    .config(f"spark.sql.{CATALOG_NAME}.polaris.type", "rest")
    .config(f"spark.sql.{CATALOG_NAME}.polaris.uri", f"{POLARIS_BASE_URL}/api/catalog")
    .config(f"spark.sql.{CATALOG_NAME}.polaris.warehouse", "warehouse")
    .config(f"spark.sql.{CATALOG_NAME}.polaris.credential", f"{CLIENT_ID}:{CLIENT_SECRET}")
    .config(f"spark.sql.{CATALOG_NAME}.polaris.scope", "PRINCIPAL_ROLE:ALL")
    .config(f"spark.sql.{CATALOG_NAME}.polaris.rest.auth.type", "oauth2")
    .config(f"spark.sql.{CATALOG_NAME}.polaris.token-refresh-enabled", "true")
    .config(f"spark.sql.{CATALOG_NAME}.polaris.oauth2-server-uri", f"{POLARIS_BASE_URL}/api/catalog/v1/oauth/tokens")
    .config(f"spark.hadoop.fs.s3a.endpoint", MINIO_BASE_URL)
    .config(f"spark.hadoop.fs.s3a.access.key", MINIO_USER)
    .config(f"spark.hadoop.fs.s3a.secret.key", MINIO_PASS)
    .config(f"spark.hadoop.fs.s3a.path.style.access", "true")
    .config(f"spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .config(f"spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
    .config(f"spark.hadoop.fs.s3a.multipart.size", "128M")
    .config(f"spark.hadoop.fs.s3a.fast.upload", "true")
    .config(f"spark.hadoop.fs.s3a.fast.upload.buffer", "bytearray")
    .config(f"spark.hadoop.fs.s3a.fast.upload.active.blocks ", "4")
    .config(f"spark.hadoop.fs.s3a.connection.maximum", "200")
    .config(f"spark.hadoop.fs.s3a.connection.establish.timeout", "60000")
    .config(f"spark.hadoop.fs.s3a.connection.timeout", "120000")
    .config(f"spark.sql.{CATALOG_NAME}.polaris.s3.endpoint", MINIO_BASE_URL)
    .config(f"spark.sql.{CATALOG_NAME}.polaris.s3.access-key-id", MINIO_USER)
    .config(f"spark.sql.{CATALOG_NAME}.polaris.s3.secret-access-key", MINIO_PASS)
    .config(f"spark.sql.{CATALOG_NAME}.polaris.client.region", "us-east-1")
    .config(f"spark.sql.{CATALOG_NAME}.polaris.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")
    .config(f"spark.sql.iceberg.advisory-partition-size-bytes", "536870912")
    .getOrCreate())

# spark.sql("CREATE NAMESPACE IF NOT EXISTS polaris.db").show()
# spark.sql("CREATE TABLE IF NOT EXISTS polaris.db.example (name STRING)").show()
# spark.sql("INSERT INTO polaris.db.example VALUES ('example value')").show()
# spark.sql("SELECT * FROM polaris.db.example").show()

# Read the original Parquet Data
input_path = "/data/parquet"
df = spark.read.parquet(input_path)

df = df.sample(withReplacement=False, fraction=0.10).repartition(12)

NAMESPACE = f"{CATALOG_NAME}.my_namespace"
TABLE = f"{NAMESPACE}.my_table"

# Create the Namespace and write the table
spark.sql(f"CREATE NAMESPACE IF NOT EXISTS {NAMESPACE}")

df.writeTo(TABLE) \
    .tableProperty("write.format.default", "parquet") \
    .tableProperty("write.parquet.compression-codec", "zstd") \
    .tableProperty("write.target-file-size-bytes", "536870912") \
    .create()

spark.sql(f"SELECT count(*) FROM {TABLE}").show()

# spark.sql(f"DROP TABLE {TABLE} PURGE").show()
# spark.sql(f"DROP NAMESPACE {NAMESPACE}")
