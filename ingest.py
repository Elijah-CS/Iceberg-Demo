from pyspark.sql import SparkSession

CLIENT_ID = "94f1f5b42affc2d8"
CLIENT_SECRET = "a004634f2f14141c3c00b82a5734895b"

spark_packages = [
    "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.7.0", # Recommend 1.7.0 for 1.3.0 Polaris
    "org.apache.iceberg:iceberg-aws-bundle:1.7.0",
    "org.apache.polaris:polaris-spark-3.5_2.12:1.3.0-incubating" # CRITICAL: New Spark client JAR
]

spark = (SparkSession.builder
    .config("spark.jars.packages", ",".join(spark_packages))
    .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.0,org.apache.iceberg:iceberg-aws-bundle:1.10.0")
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
    .config("spark.sql.catalog.polaris", "org.apache.polaris.spark.SparkCatalog")
    .config("spark.sql.catalog.polaris.type", "rest")
    .config("spark.sql.catalog.polaris.uri", "http://localhost:8181/api/catalog")
    .config("spark.sql.catalog.polaris.warehouse", "warehouse")
    .config("spark.sql.catalog.polaris.credential", f"{CLIENT_ID}:{CLIENT_SECRET}")
    .config("spark.sql.catalog.polaris.scope", "PRINCIPAL_ROLE:ALL")
    .config("spark.sql.catalog.polaris.rest.auth.type", "oauth2")
    .config("spark.sql.catalog.polaris.token-refresh-enabled", "true")
    .config("spark.sql.catalog.polaris.oauth2-server-uri", "http://localhost:8181/api/catalog/v1/oauth/tokens")
    .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000")
    .config("spark.hadoop.fs.s3a.access.key", "admin")
    .config("spark.hadoop.fs.s3a.secret.key", "password")
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
    .config("spark.sql.catalog.polaris.s3.endpoint", "http://localhost:9000")
    .config("spark.sql.catalog.polaris.s3.path-style-access", "true")
    .config("spark.sql.catalog.polaris.s3.access-key-id", "admin")
    .config("spark.sql.catalog.polaris.s3.secret-access-key", "password")
    .config("spark.sql.catalog.polaris.client.region", "us-east-1")
    .config("spark.sql.catalog.polaris.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")
    .getOrCreate())

spark.sql("CREATE NAMESPACE IF NOT EXISTS polaris.db").show()
spark.sql("CREATE TABLE IF NOT EXISTS polaris.db.example (name STRING)").show()
spark.sql("INSERT INTO polaris.db.example VALUES ('example value')").show()
spark.sql("SELECT * FROM polaris.db.example").show()