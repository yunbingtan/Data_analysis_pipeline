#!/usr/bin/env bash
set -euo pipefail

LOCAL_UID="${LOCAL_UID:-1000}"
LOCAL_GID="${LOCAL_GID:-1000}"
USERNAME="${CONTAINER_USER_NAME:-appuser}"
GROUPNAME="${CONTAINER_GROUP_NAME:-appgroup}"

if [[ "$LOCAL_UID" == "0" ]]; then
  exec "$@"
fi

existing_group="$(getent group "$LOCAL_GID" | cut -d: -f1 || true)"
if [[ -n "$existing_group" ]]; then
  GROUPNAME="$existing_group"
elif ! getent group "$GROUPNAME" >/dev/null 2>&1; then
  groupadd --gid "$LOCAL_GID" "$GROUPNAME"
fi

existing_user="$(getent passwd "$LOCAL_UID" | cut -d: -f1 || true)"
if [[ -n "$existing_user" ]]; then
  USERNAME="$existing_user"
elif ! getent passwd "$USERNAME" >/dev/null 2>&1; then
  useradd --uid "$LOCAL_UID" --gid "$LOCAL_GID" --create-home --shell /bin/bash "$USERNAME"
fi

HOME_DIR="$(getent passwd "$USERNAME" | cut -d: -f6)"
mkdir -p "$HOME_DIR" /workspace/airflow/logs /workspace/airflow/plugins /workspace/airflow/dags
chown "$LOCAL_UID:$LOCAL_GID" "$HOME_DIR"

export HOME="$HOME_DIR"

exec gosu "$USERNAME" "$@"
