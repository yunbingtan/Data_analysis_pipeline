'''Airflow DAG to run dbt build for the repo-local dbt project.'''
from datetime import timedelta
from pathlib import Path

import pendulum
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

REPO_ROOT = Path(__file__).resolve().parents[2]
DBT_PROJECT_DIR = REPO_ROOT / "jaffle-shop-main"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': pendulum.datetime(2025, 6, 1, tz="UTC"),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='dbt_build_dag',
    description='Run dbt build for the dbt project in this repository',
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=['dbt'],
) as dag:
    dbt_deps = BashOperator(
        task_id='dbt_deps',
        bash_command=(
            f'cd "{DBT_PROJECT_DIR}" && '
            'dbt deps --project-dir . --profiles-dir .'
        ),
    )

    dbt_build = BashOperator(
        task_id='dbt_build',
        bash_command=(
            f'cd "{DBT_PROJECT_DIR}" && '
            'dbt build --project-dir . --profiles-dir .'
        ),
    )

    dbt_deps >> dbt_build
