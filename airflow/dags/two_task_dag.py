'''Example DAG II'''
from datetime import timedelta
from pathlib import Path
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
import pendulum

# The data directory is mounted at /opt/airflow/data, which maps to the repo's data/ directory
OUTPUT_FILE = Path("/opt/airflow/data/output/two_task_dag.txt")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': pendulum.datetime(2025, 6, 1, tz="UTC"),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='two_task_dag',
    description='A simple DAG with two tasks',
    schedule=None,
    catchup=False,
    default_args=default_args,
) as dag:
    
    task0 = BashOperator(
        task_id='task_one',
        bash_command=f'mkdir -p "{OUTPUT_FILE.parent}" && echo "This is the first task in a simple DAG with two tasks!" > "{OUTPUT_FILE}"',
    )

    task1 = BashOperator(
        task_id='task_two',
        bash_command=f'sleep 5 && echo "This is the second task, which depends on the first task!" >> "{OUTPUT_FILE}"',
    )

    task0 >> task1