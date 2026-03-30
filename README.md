This repo showcases an Airflow-orchestrated data pipeline and a GitHub Actions CI workflow.

## Environment setup
This project now uses Docker instead of a local `.venv`.

Prerequisites:
```
docker
docker compose
```

Build the image the first time:
```bash
./scripts/docker-compose.sh build
```

Run an ad hoc Python command inside the container:
```bash
./scripts/python.sh scripts/test_run.py
```

Open a shell in the container:
```bash
./scripts/docker-compose.sh run --rm app bash
```

Exit container:
```bash
exit
```

## Airflow
Initialize the local Airflow metadata DB under the repo:
```bash
./scripts/airflow.sh db migrate
```

Start Airflow standalone on `http://localhost:8080`:
```bash
./scripts/airflow-standalone.sh
```

Run other Airflow CLI commands with the repo-local config:
```bash
./scripts/airflow.sh dags list
./scripts/airflow.sh dags test one_task_dag 2024-01-01
```

If example DAGs still appear, reset the local Airflow DB and start again:
```bash
./scripts/airflow-reset-db.sh
./scripts/airflow-standalone.sh
```

Run Airflow in the background:
```bash
nohup ./scripts/airflow-standalone.sh > airflow/standalone.out 2>&1 &
```

View background logs:
```bash
tail -f airflow/standalone.out
```

Stop the standalone container:
```bash
./scripts/docker-compose.sh down
```

Syntax-check a DAG module in the same containerized environment:
```bash
./scripts/python.sh -W ignore airflow/dags/one_task_dag.py
```

## SQLite
View DB tables:
```bash
sqlite3 data/manual-load-db.db "select name from sqlite_master where type='table' or type='view';"
```

View table schema:
```bash
sqlite3 data/manual-load-db.db ".schema top_level_domains"
```

View rows:
```bash
sqlite3 -header -column data/manual-load-db.db "select * from top_level_domains limit 20;"
```

## DBT
Run dbt deps
```bash
./scripts/docker-compose.sh run --rm app dbt deps --project-dir jaffle-shop-main --profiles-dir jaffle-shop-main
```

Run dbt seed for jaffle-shop-main:
```bash
./scripts/docker-compose.sh run --rm app dbt seed --project-dir jaffle-shop-main --profiles-dir jaffle-shop-main --full-refresh --vars '{"load_source_data": true}'
```

Run dbt build for `jaffle-shop-main`:
```bash
./scripts/docker-compose.sh run --rm app dbt build --project-dir jaffle-shop-main --profiles-dir jaffle-shop-main
```

Trigger the repo-local dbt build from Airflow:
```bash
./scripts/airflow.sh dags test dbt_build_dag 2024-01-01
```

Or start Airflow and trigger `dbt_build_dag` from the UI at `http://localhost:8080`.
