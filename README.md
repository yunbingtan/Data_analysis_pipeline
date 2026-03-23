This repo showcases an Airflow-orchestrated data pipeline and a GitHub Actions CI workflow.

## Environment setup
This project now uses Docker instead of a local `.venv`.

Prerequisites:
```
docker
docker compose
```

Build the image the first time (or after requirements changes):
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

## PostgreSQL
PostgreSQL runs on the host machine from `data/postgres`. The Docker containers connect to it through `host.docker.internal`.

Initialize PostgreSQL in the repo:
```bash
./scripts/postgres-init.sh
```

Start PostgreSQL:
```bash
./scripts/postgres-start.sh
```

If PostgreSQL is already initialized under `data/postgres`, just start it:
```bash
./scripts/postgres-start.sh
```

Verify the connection:
```bash
psql -U dbt -d ecom -c "SELECT current_database(), current_user;"
lsof -nP -iTCP:5432 -sTCP:LISTEN
tail -n 20 data/postgres/server.log
```

The dbt profile in Docker points at `host.docker.internal:5432`, so once the host PostgreSQL server is running you can use the existing Docker commands for `dbt deps`, `dbt seed`, and `dbt build`.

View DB tables:
```bash
psql -U dbt -d ecom -c "\dt main.*"
psql -U dbt -d ecom -c "\dv main.*"
psql -U dbt -d ecom -c "\ds main.*"
```

View table schema:
```bash
psql -U dbt -d ecom -c "\d main.top_level_domains"
```

View rows:
```bash
psql -U dbt -d ecom -c "SELECT * FROM main.top_level_domains LIMIT 20;"
```

Stop the local PostgreSQL server:
```bash
./scripts/postgres-stop.sh
```

## DBT
Run dbt deps
```bash
./scripts/docker-compose.sh run --rm app dbt deps --project-dir jaffle-shop-main --profiles-dir jaffle-shop-main
```

Check the container can reach PostgreSQL:
```bash
./scripts/docker-compose.sh run --rm app dbt debug --project-dir jaffle-shop-main --profiles-dir jaffle-shop-main
```

Run dbt seed for jaffle-shop-main:
```bash
./scripts/docker-compose.sh run --rm app dbt seed --project-dir jaffle-shop-main --profiles-dir jaffle-shop-main --vars '{"load_source_data": true}'
```

Run dbt build for `jaffle-shop-main`:
```bash
./scripts/docker-compose.sh run --rm app dbt build --project-dir jaffle-shop-main --profiles-dir jaffle-shop-main
```

**Note**: The project now uses PostgreSQL, allowing Python models (.py files) in addition to SQL models.
