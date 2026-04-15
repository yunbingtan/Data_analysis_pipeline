'''Challenge ETL DAG example'''
from datetime import timedelta, date
import pendulum
from pathlib import Path
import pandas as pd
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_URL = "https://raw.githubusercontent.com/LinkedInLearning/hands-on-introduction-data-engineering-4395021/main/data/constituents.csv"
INPUT_FILE = REPO_ROOT / 'data' / 'input' / 'sample_constituents.csv'
OUTPUT_FILE = REPO_ROOT / 'data' / 'output' / 'transformed_sample_constituents.csv'
DB_FILE = REPO_ROOT / 'data' / 'manual-load-db.db'
TABLE_NAME = 'constituents'

def transform_data():
    df = pd.read_csv(INPUT_FILE)
    df = df.groupby('Sector').size().reset_index(name='Count')
    df['Date'] = date.today().strftime('%Y-%m-%d')
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

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

mkdir -p "{INPUT_FILE.parent}"
echo "Extracting data from {INPUT_FILE}..."

curl -fsSL "{SOURCE_URL}" -o "{INPUT_FILE}"
""".strip(),
    )

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
    )

    load_task = BashOperator(
        task_id='load_data',
        bash_command=f"""
set -euo pipefail

mkdir -p "{DB_FILE.parent}"

sqlite3 "{DB_FILE}" <<SQL
CREATE TABLE IF NOT EXISTS {TABLE_NAME}(
    Sector VARCHAR(100),
    Count INTEGER,
    Date DATE
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_constituents_sector ON {TABLE_NAME}(Sector, Date);

DROP TABLE IF EXISTS constituents_staging;
CREATE TABLE constituents_staging(
    Sector VARCHAR(100),
    Count INTEGER,
    Date DATE
);

.mode csv
.import --skip 1 "{OUTPUT_FILE}" constituents_staging

INSERT OR IGNORE INTO {TABLE_NAME} (Sector, Count, Date)
SELECT Sector, Count, Date
FROM constituents_staging;

DROP TABLE constituents_staging;
SQL
""".strip(),
    )

    extract_task >> transform_task >> load_task
