
# Weather Data Pipeline

A Python and PySpark data engineering project that collects
historical weather data, validates it, transforms it into
Parquet format, and performs SQL-based analysis.

## Pipeline

1. Extract hourly weather data from the Open-Meteo Archive API.
2. Save raw API responses as JSON.
3. Transform nested JSON data into a tabular structure using PySpark.
4. Validate required columns, null values, and measurement ranges.
5. Remove duplicate city-timestamp records.
6. Store processed data in Parquet format.
7. Run SQL queries to analyze temperature, precipitation,
   and wind speed.

## Technologies

- Python
- REST API
- PySpark
- SQL
- Parquet
- pytest

## Project structure

```text
weather-data-pipeline/
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── analyze.py
│   ├── check_out.py
│   └── run_pipeline.py
├── tests/
├── sql/
│   └── analysis.sql
├── data/
├── .gitignore
└── README.md
```

## Running the project

Activate the Python virtual environment and install the
required dependencies.

Run the pipeline from the project root:

```bash
python src/run_pipeline.py
```

Run tests:

```bash
python -m pytest -v
```

## Data source

Historical weather data is obtained from the
[Open-Meteo Archive API](https://open-meteo.com/en/docs/historical-weather-api).

## Current scope

The pipeline runs locally and processes hourly weather
observations for three Polish cities over a selected date range.
