from pyspark.sql import SparkSession

CLIENT_ID = "0c339df8494951a5"
CLIENT_SECRET = "a41cdc2e25717481a3f9740b3cf0eba6"

spark = (SparkSession.builder
    .config("spark.jars.packages", "org.apache.polaris:polaris-spark-3.5_2.12:1.1.0-incubating,org.apache.iceberg:iceberg-aws-bundle:1.10.0,org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.0")
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
    .config("spark.sql.catalog.polaris", "org.apache.polaris.spark.SparkCatalog")
    .config("spark.sql.catalog.polaris.uri", "http://localhost:8181/api/catalog")
    .config("spark.sql.catalog.polaris.warehouse", "warehouse")
    .config("spark.sql.catalog.polaris.credential", f"{CLIENT_ID}:{CLIENT_SECRET}")
    .config("spark.sql.catalog.polaris.scope", "PRINCIPAL_ROLE:ALL")
    .config("spark.sql.catalog.polaris.header.X-Iceberg-Access-Delegation", "vended-credentials")
    .config("spark.sql.catalog.polaris.rest.auth.type", "oauth2")
    .config("spark.sql.catalog.polaris.token-refresh-enabled", "true")
    .config("spark.sql.catalog.polaris.oauth2-server-uri", "http://localhost:8181/api/catalog/v1/oauth/tokens")
    .getOrCreate())

spark.sql("CREATE NAMESPACE IF NOT EXISTS polaris.db").show()
spark.sql("CREATE TABLE IF NOT EXISTS polaris.db.example (name STRING)").show()
spark.sql("INSERT INTO polaris.db.example VALUES ('example value')").show()
spark.sql("SELECT * FROM polaris.db.example").show()