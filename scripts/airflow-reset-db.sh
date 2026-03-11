#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export AIRFLOW_HOME="$REPO_ROOT/airflow"
export AIRFLOW_CONFIG="$AIRFLOW_HOME/airflow.cfg"
export AIRFLOW__CORE__LOAD_EXAMPLES=False

rm -f "$AIRFLOW_HOME/airflow.db"
rm -rf "$AIRFLOW_HOME/logs"

mkdir -p "$AIRFLOW_HOME/dags" "$AIRFLOW_HOME/plugins"

"$REPO_ROOT/scripts/airflow.sh" db migrate
