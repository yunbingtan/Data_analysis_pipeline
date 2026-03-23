FROM python:3.11-slim

ARG AIRFLOW_VERSION=3.1.7
ARG PYTHON_VERSION=3.11

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    AIRFLOW_HOME=/workspace/airflow \
    AIRFLOW_CONFIG=/workspace/airflow/airflow.cfg \
    AIRFLOW__CORE__LOAD_EXAMPLES=False \
    AIRFLOW__CORE__SIMPLE_AUTH_MANAGER_PASSWORDS_FILE=/workspace/airflow/simple_auth_manager_passwords.json.generated \
    PYTHONPATH=/workspace

WORKDIR /workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash gosu graphviz git postgresql-client libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
COPY scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN pip install --upgrade pip setuptools wheel \
    && pip install "apache-airflow==${AIRFLOW_VERSION}" \
        --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt" \
    && pip install -r /tmp/requirements.txt \
    && chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["bash"]
