from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("MinIOTest").getOrCreate()

data = [("Alice", 28), ("Bob", 34)]
df = spark.createDataFrame(data, ["name", "age"])

# Write to MinIO
df.write.mode("overwrite").parquet("s3a://my-bucket/test-parquet")

# Read back
df2 = spark.read.parquet("s3a://my-bucket/test-parquet")
df2.show()
