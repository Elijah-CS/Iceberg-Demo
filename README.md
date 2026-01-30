# Spark
```
pyspark \
  --master local[10] \
  --driver-memory 1G \
  --num-executors 4 \
  --executor-memory 1G \
  --executor-cores 4 \
  --conf "spark.driver.maxResultSize=5G" \
  --conf "spark.executor.memoryOverhead=5G" \
  --conf "spark.driver.memoryOverhead=5G" \
  --conf "spark.driver.memory=5G" \
  --jars <iceberg-aws-bundle:1.7.0>,<iceberg-spark-runtime:1.7.0>
```
