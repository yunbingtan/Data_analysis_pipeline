"""Airflow DAG to run dbt deps and dbt seed inside the dbt container."""
from datetime import timedelta
import os
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator

from dbt_container_utils import run_dbt

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": pendulum.datetime(2025, 6, 1, tz="UTC"),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="dbt_seed_dag",
    description="Run dbt deps and dbt seed inside the dbt container",
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["dbt"],
) as dag:
    def run_deps() -> None:
        run_dbt("deps")

    dbt_deps = PythonOperator(
        task_id="dbt_deps",
        python_callable=run_deps,
    )

    def run_seed() -> None:
        run_dbt(
            "seed",
            extra_args=[
                "--full-refresh",
                "--vars",
                '{"load_source_data": true}',
            ],
        )

    dbt_seed = PythonOperator(
        task_id="dbt_seed",
        python_callable=run_seed,
    )

    dbt_deps >> dbt_seed
