#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="${ROOT_DIR}/data/postgres"

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
  exit 1
}

export PATH="$(find_pg_bin):${PATH}"

if [ ! -f "${DATA_DIR}/PG_VERSION" ]; then
  echo "PostgreSQL is not initialized in ${DATA_DIR}." >&2
  echo "Run ./scripts/postgres-init.sh first." >&2
  exit 1
fi

pg_ctl -D "${DATA_DIR}" -l "${DATA_DIR}/server.log" start
