#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export AIRFLOW_HOME="$REPO_ROOT/airflow"
mkdir -p "$AIRFLOW_HOME/dags" "$AIRFLOW_HOME/plugins"

exec "$REPO_ROOT/scripts/docker-compose.sh" up --build airflow-standalone
