This repo will showcase leveraging airflow to orchstrate data pipeline and github action to set up CI workflow.

###  Activate python virtual environment
```
source .venv/bin/activate
```
### Install dependence
```
pip install -r requirements.txt
```
### Execute
```
python run.py
```

## Airflow
### Install
```
pip install --upgrade pip setuptools wheel

AIRFLOW_VERSION=3.1.7
PYTHON_VERSION=3.11
pip install "apache-airflow==$AIRFLOW_VERSION" \
--constraint "https://raw.githubusercontent.com/apache/airflow/constraints-$AIRFLOW_VERSION/constraints-$PYTHON_VERSION.txt"
```

### Set up
```
export AIRFLOW_HOME=$(pwd)/airflow
export AIRFLOW_CONFIG=$AIRFLOW_HOME/airflow.cfg
export AIRFLOW__CORE__LOAD_EXAMPLES=False
./scripts/airflow.sh db migrate
```

### Run
create a new terminal with virtural env activated
```
./scripts/airflow-standalone.sh
```

or 
```
export AIRFLOW_HOME=$(pwd)/airflow
airflow standalone
```

To run Airflow CLI commands with the same config (for example, listing DAGs):
```
./scripts/airflow.sh dags list
```

If you see Airflow mentioning `/Users/yunbingtan/airflow/...`, you started Airflow without these scripts (default `AIRFLOW_HOME` is `~/airflow`). Always use the scripts above, or export `AIRFLOW_HOME=$(pwd)/airflow` before running `airflow`.

If you can still see example DAGs, they are already stored in your local metadata DB. Reset the local Airflow DB and start again:
```
./scripts/airflow-reset-db.sh
./scripts/airflow-standalone.sh
```

### run in background
```
nohup ./scripts/airflow-standalone.sh > airflow/standalone.out 2>&1 &
```
### see detail of backgroun run
```
tail -f airflow/standalone.out
```
### kill backgroun run
`pkill -f "airflow standalone"` (or find the PID with `ps aux | grep -Ei "airflow|uvicorn|gunicorn" | grep -v grep` and `kill <pid>` or `kill -9 <pid>`)

### Syntac checkin for dag
```
python -W ignore airflow/dags/one_task_dag.py
```


## SQLite
### View db
```
sqlite3 data/manual-load-db.db "select name from sqlite_master where type='table' or type='view';"
```
### View table schema
```
sqlite3 data/manual-load-db.db ".schema top_level_domains"
```
### View rows
```
sqlite3 -header -column data/manual-load-db.db "select * from top_level_domains limit 20;"
```
