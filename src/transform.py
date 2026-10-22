
import logging

from pyspark.sql import SparkSession, DataFrame, functions as F


RAW_PATH = [
    "data/raw/warsaw_weather.json",
    "data/raw/krakow_weather.json",
    "data/raw/gdansk_weather.json",
]
OUTPUT_PATH = "data/processed/weather"

REQUIRED_COLUMNS = [
    "city",
    "timestamp",
    "temperature_2m",
    "precipitation",
    "wind_speed_10m",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def transform_weather(raw_df: DataFrame) -> DataFrame:
    """Convert nested hourly API data into one row per city and timestamp."""
    hourly_arrays = F.arrays_zip(
        F.col("hourly.time").alias("timestamp"),
        F.col("hourly.temperature_2m").alias("temperature_2m"),
        F.col("hourly.precipitation").alias("precipitation"),
        F.col("hourly.wind_speed_10m").alias("wind_speed_10m"),
    )

    return (
        raw_df
        .select("city", F.explode(hourly_arrays).alias("record"))
        .select(
            "city",
            F.to_timestamp("record.timestamp").alias("timestamp"),
            F.col("record.temperature_2m").cast("double").alias(
                "temperature_2m"
            ),
            F.col("record.precipitation").cast("double").alias(
                "precipitation"
            ),
            F.col("record.wind_speed_10m").cast("double").alias(
                "wind_speed_10m"
            ),
        )
    )


def validate_weather(df: DataFrame) -> None:
    """Raise an error when required data quality rules are violated."""
    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    null_counts = df.select(
        *[
            F.sum(F.col(column).isNull().cast("int")).alias(column)
            for column in REQUIRED_COLUMNS
        ]
    ).first().asDict()

    null_counts = {
        column: count or 0
        for column, count in null_counts.items()
    }

    if any(null_counts.values()):
        raise ValueError(f"Null values found: {null_counts}")

    invalid_condition = (
        (F.col("temperature_2m") < -90)
        | (F.col("temperature_2m") > 60)
        | (F.col("precipitation") < 0)
        | (F.col("wind_speed_10m") < 0)
        | (F.col("wind_speed_10m") > 300)
    )

    invalid_count = df.filter(invalid_condition).count()

    if invalid_count:
        raise ValueError(
            f"Found {invalid_count} records with invalid measurements"
        )


def main() -> None:
    spark = (
        SparkSession.builder
        .appName("WeatherDataPipeline")
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    try:
        raw_df = (
            spark.read
            .option("multiLine", True)
            .json(RAW_PATH)
        )

        weather_df = transform_weather(raw_df)

        initial_count = weather_df.count()
        logger.info("Transformed records before deduplication: %d", initial_count)

        # Validate measurements before removing duplicates.
        validate_weather(weather_df)
        logger.info("Data quality validation passed")

        # Keep only one record for each city and timestamp.
        weather_df = weather_df.dropDuplicates(["city", "timestamp"])
        final_count = weather_df.count()

        logger.info("Removed duplicates: %d", initial_count - final_count)

        # Save transformed data in Parquet format.
        (
            weather_df.write
            .mode("overwrite")
            .parquet(OUTPUT_PATH)
        )

        logger.info("Saved Parquet data to %s", OUTPUT_PATH)
        logger.info("Final row count: %d", final_count)

        weather_df.orderBy("city", "timestamp").show(10, truncate=False)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
