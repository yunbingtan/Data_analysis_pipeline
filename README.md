This repository sets up a local data analysis pipeline with Docker Compose. It combines Apache Airflow for orchestration, dbt for transformations, and PostgreSQL for storage, with each service running in containers.

The repo also includes:
- Airflow DAGs for ETL and dbt execution
- A dbt sample project in `dbt/jaffle-shop`
- A separate PostgreSQL instance for dbt development
- Adminer for inspecting databases in the browser
- A lightweight Python analysis container for notebooks and ad hoc scripts

## Repository structure
- `airflow/`: custom Airflow image, config, and DAGs
- `dbt/jaffle-shop/`: dbt project, seeds, models, and profile
- `data/`: local input, output, and seed data mounted into containers
- `scripts/`: Python analysis environment, helper files, and notebook support
- `docker-compose.yaml`: local multi-container stack definition

## Services in Docker Compose
- `airflow-apiserver`, `airflow-scheduler`, `airflow-worker`, `airflow-triggerer`, `airflow-dag-processor`: Airflow runtime services
- `postgres`: metadata database for Airflow
- `redis`: Celery broker for Airflow
- `dbt-postgres`: PostgreSQL database used by the dbt project
- `dbt`: long-running dbt container used by Airflow DAGs and manual dbt commands
- `adminer`: database UI exposed on `http://localhost:8081`
- `python-analysis`: Python environment for notebooks and analysis scripts

## What this repo demonstrates
- Running Airflow locally with Docker Compose
- Executing ETL-style DAGs that ingest and load data into PostgreSQL
- Running `dbt deps`, `dbt seed`, and `dbt build` from Airflow
- Developing and testing data transformations in an isolated local environment

## Prerequisites
- docker
- docker compose

## Set up
Copy the environment template and update usernames/passwords as needed:
```bash
cp .env_copy .env
```

> [!CAUTION]
> The airflow database username, password, and db name (`_AIRFLOW_DB_USERNAME`, `_AIRFLOW_DB_PASSWORD` and `_AIRFLOW_DB_NAME`) and dbt database username, password, and db name (`_DBT_DB_USERNAME`, `_DBT_DB_PASSWORD`, and `_DBT_DB_NAME`) will be saved in the mounted local folders.
>
> If you want to change them after build: <br>
> Option 1: remove everything in the folder and run build again<br>
> Option 2: change the password in db and update the docker-compose.yaml

## Run and build the image
```bash
docker compose up --build -d
```

After startup:
- Airflow API/UI is available on `http://localhost:8080`
- Adminer is available on `http://localhost:8081`
- Jupyter can be started from the `python-analysis` container on port `8888`

## Run the image
```bash
docker compose up
```

## Stop and clean up
```bash
docker compose down --volumes --rmi all
```

## Run container command
Enter terminal
```bash
docker compose exec <container id or name> bash
```
Exit terminal
```bash
exit
```

## Example commands
Test dag
```bash
docker compose exec airflow-apiserver airflow dags test basic_etl_dag 2026-05-01
```

Test dbt
```bash
docker compose exec dbt dbt deps
docker compose exec dbt dbt seed  --vars '{"load_source_data": true}'
docker compose exec dbt dbt build
```

Run jupyter notebook in `scripts`
```bash
docker compose exec python-analysis jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root

```
