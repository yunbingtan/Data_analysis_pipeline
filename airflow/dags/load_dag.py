'''Load DAG'''
from pathlib import Path

import pendulum
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from datetime import timedelta

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = REPO_ROOT / 'data' / 'output' / 'transformed_sample.csv'
DB_FILE = REPO_ROOT / 'data' / 'manual-load-db.db'
TABLE_NAME = 'top_level_domains'

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
    'load_dag',
    default_args=default_args,
    description='A simple load DAG',
    schedule=None,
    catchup=False
) as dag:
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
CREATE UNIQUE INDEX IF NOT EXISTS ux_top_level_domains_domain ON {TABLE_NAME}(Domain);

DROP TABLE IF EXISTS top_level_domains_staging;
CREATE TABLE top_level_domains_staging(
    Domain VARCHAR(30),
    Type VARCHAR(30),
    SponsoringOrganization VARCHAR(30),
    Date DATE
);

.mode csv
.import --skip 1 "{INPUT_FILE}" top_level_domains_staging

INSERT OR IGNORE INTO {TABLE_NAME} (Domain, Type, SponsoringOrganization, Date)
SELECT Domain, Type, SponsoringOrganization, Date
FROM top_level_domains_staging;

DROP TABLE top_level_domains_staging;
SQL
""".strip(),
    )
