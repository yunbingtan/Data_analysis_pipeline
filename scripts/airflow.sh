#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export AIRFLOW_HOME="$REPO_ROOT/airflow"
export AIRFLOW_CONFIG="$AIRFLOW_HOME/airflow.cfg"

# Ensure Airflow's built-in example/tutorial DAGs are not loaded.
export AIRFLOW__CORE__LOAD_EXAMPLES=False

# Ensure the SimpleAuthManager password file lives under this repo's AIRFLOW_HOME.
export AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_PASSWORDS_FILE="$AIRFLOW_HOME/simple_auth_manager_passwords.json.generated"

mkdir -p "$AIRFLOW_HOME/dags" "$AIRFLOW_HOME/plugins"

exec "$REPO_ROOT/scripts/docker-compose.sh" run --build --rm app airflow "$@"
