from pyspark.sql import SparkSession
import os

# --- Spark Session Configuration ---
spark = SparkSession.builder \
    .appName("MinIOIntegration") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://127.0.0.1:9000") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
    .config("spark.hadoop.fs.s3a.fast.upload", "true") \
    .config("spark.hadoop.fs.s3a.connection.establish.timeout", "30000") \
    .config("spark.hadoop.fs.s3a.connection.timeout", "200000") \
    .config("spark.hadoop.fs.s3a.threads.keepalivetime", "60000") \
    .config("spark.hadoop.fs.s3a.multipart.purge.age", "86400000") \
    .config(
        "spark.hadoop.fs.s3a.aws.credentials.provider",
        "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider"
    ) \
    .config("spark.sql.execution.pyspark.udf.faulthandler.enabled", "true") \
    .config("spark.python.worker.faulthandler.enabled", "true") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.6,com.amazonaws:aws-java-sdk-bundle:1.12.607") \
    .getOrCreate()

print("SparkSession created successfully.")

# --- Data operations ---
data = [("server1", 80), ("server2", 65)]
df = spark.createDataFrame(data, ["server_name", "cpu_utilization"])

print("DataFrame created.")
df.show()

try:
    print(f"Attempting to write DataFrame to s3a://nnmi-data/sample_parquet...")
    df.repartition(1).write.mode("overwrite").parquet("s3a://nnmi-data/sample_parquet")
    print("DataFrame written to MinIO successfully.")
except Exception as e:
    print(f"Error writing to MinIO: {e}")
    raise

try:
    print(f"Attempting to read DataFrame from s3a://nnmi-data/sample_parquet...")
    df2 = spark.read.parquet("s3a://nnmi-data/sample_parquet")
    print("DataFrame read from MinIO successfully.")
    df2.show()
except Exception as e:
    print(f"Error reading from MinIO: {e}")
    raise

spark.stop()
print("SparkSession stopped.")