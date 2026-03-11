'''Basic ETL DAG example'''
from datetime import timedelta, date
import pendulum
from pathlib import Path
import pandas as pd
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_URL = "https://raw.githubusercontent.com/LinkedInLearning/hands-on-introduction-data-engineering-4395021/main/data/top-level-domain-names.csv"
INPUT_FILE = REPO_ROOT / 'data' / 'input' / 'sample.csv'
OUTPUT_FILE = REPO_ROOT / 'data' / 'output' / 'transformed_sample.csv'
DB_FILE = REPO_ROOT / 'data' / 'manual-load-db.db'
TABLE_NAME = 'top_level_domains'

def transform_data():
    df = pd.read_csv(INPUT_FILE)
    df = df[df['Type'] == 'generic']
    df['Date'] = date.today().strftime('%Y-%m-%d')
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

with DAG(
    dag_id='basic_etl_dag',
    description='A basic extract-transform-load DAG',
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
    Domain VARCHAR(30),
    Type VARCHAR(30),
    SponsoringOrganization VARCHAR(30),
    Date DATE
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_top_level_domains_domain ON {TABLE_NAME}(Domain, Date);

DROP TABLE IF EXISTS top_level_domains_staging;
CREATE TABLE top_level_domains_staging(
    Domain VARCHAR(30),
    Type VARCHAR(30),
    SponsoringOrganization VARCHAR(30),
    Date DATE
);

.mode csv
.import --skip 1 "{OUTPUT_FILE}" top_level_domains_staging

INSERT OR IGNORE INTO {TABLE_NAME} (Domain, Type, SponsoringOrganization, Date)
SELECT Domain, Type, SponsoringOrganization, Date
FROM top_level_domains_staging;

DROP TABLE top_level_domains_staging;
SQL
""".strip(),
    )

    extract_task >> transform_task >> load_task
