'''Transform DAG'''
from datetime import timedelta, date
from pathlib import Path
import pendulum
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = REPO_ROOT / 'data' / 'input' / 'sample.csv'
OUTPUT_FILE = REPO_ROOT / 'data' / 'output' / 'transformed_sample.csv'

with DAG(
    dag_id='transform_dag',
    description='A simple DAG to transform data',
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
    
    def transform_data():
        df = pd.read_csv(INPUT_FILE)
        df = df[df['Type'] == 'generic']
        df['Date'] = date.today().strftime('%Y-%m-%d')
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(OUTPUT_FILE, index=False)

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
    )   