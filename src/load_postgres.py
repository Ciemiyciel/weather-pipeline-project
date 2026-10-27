"""Load processed weather observations into PostgreSQL."""

import logging
import os

import psycopg
from psycopg import sql
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StringType,
    TimestampType,
    DateType,
    DoubleType,
    FloatType,
    IntegerType,
    LongType,
    ShortType,
    BooleanType,
)

from config import PROJECT_ROOT, PROCESSED_DATA_DIR

load_dotenv(PROJECT_ROOT / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

TABLE_NAME = "weather_observations"

TYPE_MAPPING = {
    StringType: "TEXT",
    TimestampType: "TIMESTAMP",
    DateType: "DATE",
    DoubleType: "DOUBLE PRECISION",
    FloatType: "REAL",
    IntegerType: "INTEGER",
    LongType: "BIGINT",
    ShortType: "SMALLINT",
    BooleanType: "BOOLEAN",
}


def postgres_connection():
    """Open a PostgreSQL connection using environment configuration."""
    required = ["PGHOST", "PGDATABASE", "PGUSER", "PGPASSWORD"]
    missing = [name for name in required if not os.getenv(name)]

    if missing:
        raise RuntimeError(
            f"Missing PostgreSQL settings: {', '.join(missing)}"
        )

    return psycopg.connect(
        host=os.environ["PGHOST"],
        port=os.getenv("PGPORT", "5432"),
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        connect_timeout=10,
    )


def spark_type_to_postgres(spark_type):
    """Convert a supported Spark data type to a PostgreSQL type."""
    for spark_class, postgres_type in TYPE_MAPPING.items():
        if isinstance(spark_type, spark_class):
            return postgres_type

    raise TypeError(
        f"Unsupported Spark data type: {spark_type}"
    )


def load_weather() -> int:
    parquet_path = str(PROCESSED_DATA_DIR / "weather")

    spark = (
        SparkSession.builder
        .appName("WeatherPostgresLoader")
        .getOrCreate()
    )

    try:
        df = spark.read.parquet(parquet_path)

        required_columns = {"city", "timestamp"}
        missing = required_columns - set(df.columns)

        if missing:
            raise ValueError(
                f"Parquet is missing required columns: {sorted(missing)}"
            )

        if df.filter(
            df["city"].isNull() | df["timestamp"].isNull()
        ).limit(1).count():
            raise ValueError("City and timestamp must not be null")

        fields = df.schema.fields
        columns = [field.name for field in fields]

        if len(columns) != len(set(columns)):
            raise ValueError("Duplicate column names in Parquet schema")

        column_definitions = []
        for field in fields:
            postgres_type = spark_type_to_postgres(field.dataType)
            column_definitions.append(
                sql.SQL("{} {}").format(
                    sql.Identifier(field.name),
                    sql.SQL(postgres_type),
                )
            )

        # A city and timestamp identify one hourly observation.
        column_definitions.append(
            sql.SQL("PRIMARY KEY ({}, {})").format(
                sql.Identifier("city"),
                sql.Identifier("timestamp"),
            )
        )

        create_table = sql.SQL(
            "CREATE TABLE IF NOT EXISTS {} ({})"
        ).format(
            sql.Identifier(TABLE_NAME),
            sql.SQL(", ").join(column_definitions),
        )

        update_columns = [
            column for column in columns
            if column not in {"city", "timestamp"}
        ]

        insert_statement = sql.SQL(
            "INSERT INTO {} ({}) VALUES ({}) "
            "ON CONFLICT ({}, {}) "
        ).format(
            sql.Identifier(TABLE_NAME),
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(", ").join(sql.Placeholder() for _ in columns),
            sql.Identifier("city"),
            sql.Identifier("timestamp"),
        )

        if update_columns:
            insert_statement += sql.SQL("DO UPDATE SET {}").format(
                sql.SQL(", ").join(
                    sql.SQL("{} = EXCLUDED.{}").format(
                        sql.Identifier(column),
                        sql.Identifier(column),
                    )
                    for column in update_columns
                )
            )
        else:
            insert_statement += sql.SQL("DO NOTHING")

        # This project currently has a small dataset, so collecting rows
        # locally is acceptable. For large datasets, use batch loading/COPY.
        rows = [
            tuple(row[column] for column in columns)
            for row in df.collect()
        ]

        with postgres_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(create_table)

                if rows:
                    cursor.executemany(insert_statement, rows)

                cursor.execute(
                    sql.SQL("SELECT COUNT(*) FROM {}").format(
                        sql.Identifier(TABLE_NAME)
                    )
                )
                total_rows = cursor.fetchone()[0]

        logger.info(
            "Loaded %d input rows; table now contains %d rows",
            len(rows),
            total_rows,
        )

        return total_rows

    finally:
        spark.stop()


if __name__ == "__main__":
    load_weather()
