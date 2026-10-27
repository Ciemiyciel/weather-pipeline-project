
import pytest

from pyspark.sql import SparkSession

from src.transform import transform_weather, validate_weather


@pytest.fixture(scope="module")
def spark():
    session = (
        SparkSession.builder
        .appName("WeatherValidationTests")
        .master("local[1]")
        .getOrCreate()
    )
    session.sparkContext.setLogLevel("ERROR")

    yield session

    session.stop()


def make_weather_df(spark, temperature=15.0, precipitation=0.0, wind=10.0):
    return spark.createDataFrame(
        [
            ("Warsaw", "2025-10-01 12:00:00",
             temperature, precipitation, wind)
        ],
        [
            "city",
            "timestamp",
            "temperature_2m",
            "precipitation",
            "wind_speed_10m",
        ],
    )


def test_valid_weather_passes(spark):
    df = make_weather_df(spark)

    validate_weather(df)


def test_negative_precipitation_fails(spark):
    df = make_weather_df(spark, precipitation=-1.0)

    with pytest.raises(ValueError, match="invalid measurements"):
        validate_weather(df)


def test_null_temperature_fails(spark):
    df = spark.createDataFrame(
        [
            ("Warsaw", "2025-10-01 12:00:00",
             None, 0.0, 10.0)
        ],
        """
        city STRING,
        timestamp STRING,
        temperature_2m DOUBLE,
        precipitation DOUBLE,
        wind_speed_10m DOUBLE
        """,
    )

    with pytest.raises(ValueError, match="Null values found"):
        validate_weather(df)

def test_missing_column_fails(spark):
    df = spark.createDataFrame(
        [("Warsaw", 15.0)],
        ["city", "temperature_2m"],
    )

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_weather(df)

from src.transform import transform_weather


def test_transform_weather_creates_one_row_per_timestamp(spark):
    raw_df = spark.createDataFrame(
        [
            (
                "Warsaw",
                ["2025-10-01T10:00", "2025-10-01T11:00"],
                [12.5, 13.0],
                [0.0, 0.2],
                [10.0, 12.0],
            )
        ],
        [
            "city",
            "time",
            "temperature_2m",
            "precipitation",
            "wind_speed_10m",
        ],
    )

    # Budujemy strukturę zagnieżdżoną podobną do odpowiedzi API.
    from pyspark.sql import functions as F

    raw_df = raw_df.select(
        "city",
        F.struct(
            F.col("time").alias("time"),
            F.col("temperature_2m").alias("temperature_2m"),
            F.col("precipitation").alias("precipitation"),
            F.col("wind_speed_10m").alias("wind_speed_10m"),
        ).alias("hourly"),
    )

    result = transform_weather(raw_df).orderBy("timestamp")

    rows = result.collect()

    assert len(rows) == 2
    assert rows[0]["city"] == "Warsaw"
    assert rows[0]["temperature_2m"] == 12.5
    assert rows[1]["temperature_2m"] == 13.0