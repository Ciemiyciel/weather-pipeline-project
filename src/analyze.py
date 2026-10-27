
from pathlib import Path

from pyspark.sql import SparkSession


DATA_PATH = "data/processed/weather"
SQL_PATH = Path("sql/analysis.sql")


def main() -> None:
    spark = (
        SparkSession.builder
        .appName("WeatherSQLAnalysis")
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    try:
        weather_df = spark.read.parquet(DATA_PATH)
        weather_df.createOrReplaceTempView("weather")

        sql_text = SQL_PATH.read_text(encoding="utf-8")
        queries = [
            query.strip()
            for query in sql_text.split(";")
            if query.strip()
        ]

        for number, query in enumerate(queries, start=1):
            print(f"\n--- SQL analysis {number} ---")

            result = spark.sql(query)
            result.show(100, truncate=False)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
