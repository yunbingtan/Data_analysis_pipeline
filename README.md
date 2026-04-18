This repo showcases an Airflow-orchestrated data pipeline and a GitHub Actions CI workflow.

## Prerequisites
- docker
- docker compose

## Set up
Run and update the username and password accordingly
```bash
copy .env_copy .env
```

[!NOTE] The airflow database username, password, and db name (`_AIRFLOW_DB_USERNAME`, `_AIRFLOW_DB_PASSWORD` and `_AIRFLOW_DB_NAME`) and dbt database username, password, and db name (`_DBT_DB_USERNAME`, `_DBT_DB_PASSWORD`, and `_DBT_DB_NAME`) will be saved in the mounted local folders.

If you want to change them after build:
> Option 1: remove everything in the folder and run build again<br>
> Option 2: change the password in db and update the docker-compose.yaml

## Run and build the image
```bash
docker compose up --build -d
```

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