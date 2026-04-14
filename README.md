This repo showcases an Airflow-orchestrated data pipeline and a GitHub Actions CI workflow.

## Prerequisites
- docker
- docker compose

## Set up
Run and update the username and password accordingly
```bash
copy .env_copy .env
```

## Run and build the image
```bash
docker compose up --build
```

## Run the image
```bash
docker compose up
```

## Stop and clean up
```bash
docker compose down --volumes --rmi all
```