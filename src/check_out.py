from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("CheckWeatherOutput")
    .master("local[*]")
    .getOrCreate()
)

df = spark.read.parquet("data/processed/weather")

df.printSchema()
df.show(10, truncate=False)

print("Number of rows:", df.count())

spark.stop()