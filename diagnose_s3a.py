from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("DiagnoseS3AConfig") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://127.0.0.1:9000") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

hadoopConf = spark._jsc.hadoopConfiguration()

print("\n=== Dumping all fs.s3a.* properties ===")
confEntries = hadoopConf.iterator()
while confEntries.hasNext():
    entry = confEntries.next()
    k = entry.getKey()
    v = entry.getValue()
    if "s3a" in k:
        print(f"{k} = {v}")

spark.stop()
