from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, IntegerType

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("NNMiKafkaIngest") \
    .getOrCreate()

# Optional: Log level
spark.sparkContext.setLogLevel("INFO")

# Define JSON Schema
schema = StructType() \
    .add("timestamp", StringType()) \
    .add("server_name", StringType()) \
    .add("cpu_utilization", IntegerType()) \
    .add("memory_used_mb", IntegerType()) \
    .add("network_in_kbps", IntegerType()) \
    .add("network_out_kbps", IntegerType())

# Read Stream from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "nnmi-metrics") \
    .option("startingOffsets", "latest") \
    .load()

# Extract and parse JSON
json_df = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

# Write Stream to MinIO in Parquet format
query = json_df.writeStream \
    .format("parquet") \
    .option("path", "s3a://nnmi-data/metrics/") \
    .option("checkpointLocation", "s3a://nnmi-data/checkpoints/metrics/") \
    .outputMode("append") \
    .start()

query.awaitTermination()
