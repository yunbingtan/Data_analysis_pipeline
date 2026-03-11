'''Example DAG I'''
from datetime import timedelta
from pathlib import Path
import pendulum
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_FILE = REPO_ROOT / "data" / "output" / "one_task_dag.txt"

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
    dag_id='one_task_dag',
    description='A simple DAG with one task',
    schedule=None,
    catchup=False,
    default_args=default_args,
) as dag:
    
    task1 = BashOperator(
        task_id='one_task',
        bash_command=f'mkdir -p "{OUTPUT_FILE.parent}" && echo "This is a simple DAG with one task!" > "{OUTPUT_FILE}"',
    )
