#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="${ROOT_DIR}/data/postgres"
DB_NAME="${POSTGRES_DB:-ecom}"
DB_USER="${POSTGRES_USER:-dbt}"
DB_PASSWORD="${POSTGRES_PASSWORD:-dbt_password}"

find_pg_bin() {
  if command -v brew >/dev/null 2>&1; then
    for formula in postgresql postgresql@18 postgresql@17 postgresql@16 postgresql@15; do
      if prefix="$(brew --prefix "$formula" 2>/dev/null)" && [ -x "${prefix}/bin/pg_ctl" ]; then
        printf '%s\n' "${prefix}/bin"
        return 0
      fi
    done
  fi

  echo "Unable to find PostgreSQL binaries via Homebrew." >&2
  echo "Install PostgreSQL with Homebrew first, for example: brew install postgresql" >&2
  exit 1
}

export PATH="$(find_pg_bin):${PATH}"

mkdir -p "${ROOT_DIR}/data"

if [ ! -f "${DATA_DIR}/PG_VERSION" ]; then
  mkdir -p "${DATA_DIR}"
  initdb -D "${DATA_DIR}"
fi

perl -0pi -e "s/^#?listen_addresses\s*=.*$/listen_addresses = '*'/" "${DATA_DIR}/postgresql.conf"

if ! grep -Fq "host    all    all    0.0.0.0/0    scram-sha-256" "${DATA_DIR}/pg_hba.conf"; then
  printf '\nhost    all    all    0.0.0.0/0    scram-sha-256\n' >> "${DATA_DIR}/pg_hba.conf"
fi

if ! grep -Fq "host    all    all    ::/0         scram-sha-256" "${DATA_DIR}/pg_hba.conf"; then
  printf 'host    all    all    ::/0         scram-sha-256\n' >> "${DATA_DIR}/pg_hba.conf"
fi

if ! pg_ctl -D "${DATA_DIR}" status >/dev/null 2>&1; then
  pg_ctl -D "${DATA_DIR}" -l "${DATA_DIR}/server.log" start
fi

psql postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='${DB_USER}'" | grep -q 1 \
  || psql postgres -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';"

psql postgres -tAc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" | grep -q 1 \
  || createdb -O "${DB_USER}" "${DB_NAME}"

echo "PostgreSQL is initialized in ${DATA_DIR}"
echo "Database: ${DB_NAME}"
echo "User: ${DB_USER}"
