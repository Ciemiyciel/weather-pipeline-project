# Weather Data Pipeline

A data engineering portfolio project that collects hourly weather data from the Open-Meteo API, processes it with PySpark, stores it in PostgreSQL, and orchestrates the workflow using Apache Airflow and Docker.

## Project Overview

The goal of this project is to build an end-to-end ETL pipeline and practice working with APIs, data transformation, relational databases, SQL analytics, containerization, and workflow orchestration.

The pipeline collects historical weather data for Warsaw, Kraków, and Gdańsk, processes the raw responses, validates the resulting dataset, and loads the data into PostgreSQL.

## Architecture

```text
Open-Meteo API
      |
      v
   Extract
      |
      v
 Raw JSON files
      |
      v
 Transform (PySpark)
      |
      v
 Parquet files
      |
      +------> SQL analysis
      |
      v
 PostgreSQL
      |
      v
 Data quality checks

Apache Airflow orchestrates the workflow.
Docker Compose runs the project services.
```

## Technologies

- **Python** — API requests, pipeline logic, and database loading.
- **PySpark / Apache Spark** — data transformation and validation.
- **SQL / PostgreSQL** — data storage, aggregation, and analytical queries.
- **Apache Airflow** — workflow orchestration and task monitoring.
- **Docker / Docker Compose** — containerized execution and service management.
- **Parquet / JSON** — raw and processed data storage.
- **Git / GitHub** — version control and project documentation.
- **GitHub Actions** — automated testing and continuous integration (CI).

## Data Source

The project uses the [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api).

The current dataset covers **1–7 October 2025** and contains hourly observations for three Polish cities:

- Warsaw
- Kraków
- Gdańsk

Weather variables include:

- Temperature at 2 metres
- Precipitation
- Wind speed at 10 metres

## Pipeline Steps

### 1. Extract

The extraction script requests historical weather data from the Open-Meteo API and saves the raw JSON responses for each city.

### 2. Transform

PySpark processes the raw data by:

- Flattening nested hourly arrays into individual records.
- Converting columns to appropriate data types.
- Validating required fields and value ranges.
- Removing duplicate city-timestamp records.
- Writing the processed dataset in Parquet format.

### 3. Analyze

SQL queries calculate weather statistics using the processed data.

Additional PostgreSQL queries demonstrate analytical SQL techniques, including aggregations, common table expressions (CTEs), window functions, rankings, and moving averages.

### 4. Load

The processed Parquet data is loaded into PostgreSQL.

The table uses a composite key based on city and timestamp. The loading logic supports upserts, allowing existing records to be updated when the same key is loaded again.

### 5. Data Quality Checks

The validation script checks the loaded dataset, including record counts, missing values, expected cities, and basic value constraints.

### 6. Orchestration

Apache Airflow orchestrates the pipeline tasks in dependency order:

`extract → transform → analyze → load → data quality checks`

The DAG can be triggered manually through the Airflow interface.

## Additional SQL Analytics

The project includes a separate SQL file for running analytical queries directly against PostgreSQL.

These queries are intended for interactive analysis and are separate from the main automated workflow.

## Testing

The project includes automated tests written with **pytest** to verify the extraction and transformation components.

To run the tests locally:

```bash
python -m pytest -v
```

### Continuous Integration (GitHub Actions)

The project uses **GitHub Actions** to automatically run tests on every push and pull request.

The workflow:
- Checks out the repository.
- Sets up Java 17, required by PySpark.
- Sets up the Python environment.
- Installs project dependencies from `requirements.txt`.
- Runs the test suite using `pytest`.

The tests run in a clean GitHub-hosted environment, helping detect errors and prevent regressions when changes are introduced.

## Running the Project

### Prerequisites

- Docker
- Docker Compose
- Git

### Setup

Clone the repository and enter the project directory:

```bash
git clone <YOUR_REPOSITORY_URL>
cd weather-data-pipeline
```

Create a local `.env` file based on `.env.example` and configure the required database settings.

Build the images and start the services:

```bash
docker compose up -d --build
```

Open the Airflow interface:

`http://localhost:8080`

Trigger the `weather_data_pipeline` DAG from the Airflow UI to execute the workflow.

To inspect the running services:

```bash
docker compose ps
```

To inspect service logs:

```bash
docker compose logs --tail=100 airflow-scheduler
```

To stop the services:

```bash
docker compose down
```

## Project Structure

```text
weather-data-pipeline/
├── .github/
│   └── workflows/
│       └── tests.yml
├── dags/
│   └── weather_pipeline.py
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── analyze.py
│   ├── load_postgres.py
│   ├── check_postgres.py
│   └── run_pipeline.py
├── sql/
│   ├── analysis.sql
│   └── postgres_analytics.sql
├── data/
│   ├── raw/
│   └── processed/
├── Dockerfile
├── Dockerfile.airflow
├── compose.yaml
├── requirements.txt
└── README.md
```
