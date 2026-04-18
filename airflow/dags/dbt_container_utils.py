"""Utilities for running dbt commands inside the long-lived dbt container."""
import os
from typing import Iterable
import docker
from docker.errors import DockerException, NotFound

DBT_CONTAINER_NAME = os.getenv("DBT_CONTAINER_NAME", "dbt")
DBT_PROJECT_NAME = os.getenv("DBT_PROJECT_NAME", "jaffle-shop")
DBT_PROJECT_DIR = os.getenv(
    "DBT_PROJECT_DIR", f"/usr/app/{DBT_PROJECT_NAME}"
)
DBT_PROFILES_DIR = os.getenv(
    "DBT_PROFILES_DIR", f"/usr/app/{DBT_PROJECT_NAME}"
)


def _get_dbt_container():
    client = docker.from_env()
    try:
        container = client.containers.get(DBT_CONTAINER_NAME)
    except NotFound as exc:
        raise RuntimeError(
            f"dbt container '{DBT_CONTAINER_NAME}' was not found. "
            "Start it with `docker compose up -d dbt`."
        ) from exc
    except DockerException as exc:
        raise RuntimeError(f"Failed to connect to Docker: {exc}") from exc

    container.reload()
    if container.status != "running":
        raise RuntimeError(
            f"dbt container '{DBT_CONTAINER_NAME}' is not running (status={container.status}). "
            "Start it with `docker compose up -d dbt`."
        )

    return container


def _run_in_container(command: list[str]) -> None:
    container = _get_dbt_container()
    result = container.exec_run(command, demux=True)
    output = result.output
    if isinstance(output, tuple):
        stdout, stderr = output
    else:
        stdout, stderr = output, None

    if stdout:
        print(stdout.decode("utf-8"), end="")
    if stderr:
        print(stderr.decode("utf-8"), end="")

    if result.exit_code is None:
        raise RuntimeError(
            f"dbt command did not return an exit code in container '{DBT_CONTAINER_NAME}': "
            f"{' '.join(command)}"
        )

    if result.exit_code != 0:
        raise RuntimeError(
            f"Command failed in dbt container with exit code {result.exit_code}: "
            f"{' '.join(command)}"
        )


def run_dbt(subcommand: str, extra_args: Iterable[str] | None = None) -> None:
    command = [
        "dbt",
        subcommand,
        "--project-dir",
        DBT_PROJECT_DIR,
        "--profiles-dir",
        DBT_PROFILES_DIR,
    ]
    if extra_args:
        command.extend(extra_args)
    _run_in_container(command)
