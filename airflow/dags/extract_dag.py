'''Extract DAG'''
from datetime import timedelta
from pathlib import Path

import pendulum
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = REPO_ROOT / 'data' / 'input' / 'sample.csv'
SOURCE_URL = "https://raw.githubusercontent.com/LinkedInLearning/hands-on-introduction-data-engineering-4395021/main/data/top-level-domain-names.csv"

with DAG(
    dag_id='extract_dag',
    description='A simple DAG to extract data',
    schedule=None,
    catchup=False,
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': pendulum.datetime(2025, 6, 1, tz="UTC"),
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5)
    },
) as dag:
    
    extract_task = BashOperator(
        task_id='extract_data',
        bash_command=f"""
set -euo pipefail

mkdir -p "{INPUT_FILE.parent}"
echo "Extracting data from {INPUT_FILE}..."

curl -fsSL "{SOURCE_URL}" -o "{INPUT_FILE}"
""".strip(),
    )
