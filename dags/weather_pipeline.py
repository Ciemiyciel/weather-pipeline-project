
from datetime import datetime

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="weather_data_pipeline",
    description="Extract, transform, analyze and load weather data",
    start_date=datetime(2026, 10, 1),
    schedule=None,
    catchup=False,
    tags=["weather", "data-engineering"],
) as dag:

    extract = BashOperator(
        task_id="extract",
        bash_command="cd /app && python src/extract.py",
    )

    transform = BashOperator(
        task_id="transform",
        bash_command="cd /app && python src/transform.py",
    )

    analyze = BashOperator(
        task_id="analyze",
        bash_command="cd /app && python src/analyze.py",
    )

    load = BashOperator(
        task_id="load",
        bash_command="cd /app && python src/load_postgres.py",
    )

    quality_checks = BashOperator(
        task_id="data_quality_checks",
        bash_command="cd /app && python src/check_postgres.py",
    )

    extract >> transform >> analyze >> load >> quality_checks



