"""Airflow DAG to run dbt deps and dbt build for a selected dbt project."""
from datetime import timedelta
import os
from pathlib import Path

import pendulum
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

DBT_PROJECT_NAME = os.getenv("DBT_PROJECT_NAME", "jaffle-shop-main")
DBT_ROOT_DIR = Path(os.getenv("DBT_ROOT_DIR", "/opt/airflow/dbt"))
DBT_PROJECT_DIR = Path(
    os.getenv("DBT_PROJECT_DIR", str(DBT_ROOT_DIR / DBT_PROJECT_NAME))
)
DBT_PROFILES_DIR = Path(
    os.getenv("DBT_PROFILES_DIR", str(DBT_PROJECT_DIR))
)

DBT_BASE_COMMAND = (
    'set -euo pipefail\n'
    'command -v dbt >/dev/null 2>&1\n'
    f'test -d "{DBT_PROJECT_DIR}"\n'
    f'test -f "{DBT_PROJECT_DIR / "dbt_project.yml"}"\n'
    f'test -d "{DBT_PROFILES_DIR}"\n'
)

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
    dag_id="dbt_build_dag",
    description="Run dbt deps and dbt build for the selected dbt project",
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["dbt"],
) as dag:
    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command=(
            DBT_BASE_COMMAND
            + f'dbt deps --project-dir "{DBT_PROJECT_DIR}" '
            + f'--profiles-dir "{DBT_PROFILES_DIR}"'
        ),
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            DBT_BASE_COMMAND
            + f'dbt build --project-dir "{DBT_PROJECT_DIR}" '
            + f'--profiles-dir "{DBT_PROFILES_DIR}"'
        ),
    )

    dbt_deps >> dbt_build
