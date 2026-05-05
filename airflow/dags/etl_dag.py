'''Challenge ETL DAG example'''
from datetime import timedelta, date
import pendulum
from pathlib import Path
import pandas as pd
import psycopg2
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from dotenv import load_dotenv
import os

load_dotenv()
REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://raw.githubusercontent.com/LinkedInLearning/hands-on-introduction-data-engineering-4395021/main/data/constituents.csv"
INPUT_FILE = REPO_ROOT / 'data' / 'input' / 'sample_constituents.csv'
OUTPUT_FILE = REPO_ROOT / 'data' / 'output' / 'transformed_sample_constituents.csv'
TABLE_NAME = 'constituents'

def transform_data():
    df = pd.read_csv(INPUT_FILE)
    df = df.groupby('Sector').size().reset_index(name='Count')
    df['Date'] = date.today().strftime('%Y-%m-%d')
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

def load_data():
    df = pd.read_csv(OUTPUT_FILE)
    
    conn = psycopg2.connect(
        host=os.getenv("_DBT_DB_HOST"),
        port=os.getenv("_DBT_DB_PORT"),
        dbname=os.getenv("_DBT_DB_NAME"),
        user=os.getenv("_DBT_DB_USERNAME"),
        password=os.getenv("_DBT_DB_PASSWORD"),
        options="-c search_path=dev"
    )
    
    with conn.cursor() as cur:
        # Create table if not exists
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                Sector VARCHAR(100),
                Count INTEGER,
                Date DATE
            )
        """)
        
        # Create unique index if not exists
        cur.execute(f"""
            CREATE UNIQUE INDEX IF NOT EXISTS ux_constituents_sector 
            ON {TABLE_NAME}(Sector, Date)
        """)
        
        # Insert data with conflict resolution
        for _, row in df.iterrows():
            cur.execute(f"""
                INSERT INTO {TABLE_NAME} (Sector, Count, Date)
                VALUES (%s, %s, %s)
                ON CONFLICT (Sector, Date) DO NOTHING
            """, (row['Sector'], row['Count'], row['Date']))
    
    conn.commit()
    conn.close()

with DAG(
    dag_id='etl_dag',
    description='Another extract-transform-load DAG',
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

echo "Extracting data from {INPUT_FILE}..."

curl -fsSL "{SOURCE_URL}" -o "{INPUT_FILE}"
""".strip(),
    )

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
    )

    load_task = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
    )

    extract_task >> transform_task >> load_task
