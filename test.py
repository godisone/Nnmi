from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, explode, col, when, size, array
from pyspark.sql.types import StructType, StringType, IntegerType, ArrayType

spark = SparkSession.builder \
    .appName("NNMiKafkaIngestFlexible") \
    .getOrCreate()

record_schema = StructType() \
    .add("timestamp", StringType()) \
    .add("server_name", StringType()) \
    .add("cpu_utilization", IntegerType()) \
    .add("memory_used_mb", IntegerType()) \
    .add("network_in_kbps", IntegerType()) \
    .add("network_out_kbps", IntegerType())

array_schema = ArrayType(record_schema)

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "nnmi-metrics") \
    .load()

json_str = col("value").cast("string")

parsed_array = from_json(json_str, array_schema)
parsed_single = from_json(json_str, record_schema)

# If array is not null, use it, else wrap single into array
final_array = when(
    size(parsed_array) > 0,
    parsed_array
).otherwise(
    array(parsed_single)
)

# Explode to rows
parsed_df = df.select(
    explode(final_array).alias("metric")
).select("metric.*")

query = parsed_df.writeStream \
    .format("parquet") \
    .option("path", "s3a://nnmi-data/metrics/") \
    .option("checkpointLocation", "s3a://nnmi-data/checkpoints/") \
    .outputMode("append") \
    .start()

query.awaitTermination()
