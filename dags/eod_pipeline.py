from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

NEON_ENV = """
    export POSTGRES_HOST=$NEON_HOST &&
    export POSTGRES_PORT=5432 &&
    export POSTGRES_USER=$NEON_USER &&
    export POSTGRES_PASSWORD=$NEON_PASSWORD &&
    export NSE_WAREHOUSE_DB=$NEON_DB &&
"""

default_args = {
    'owner': 'bhavya',
    'retries': 1
}

with DAG(
    dag_id='eod_pipeline',
    default_args=default_args,
    start_date=datetime(2026, 5, 1),
    schedule='15 10 * * 1-5',
    catchup=False,
    tags=['nse', 'eod', 'pipeline'],
) as dag:
    
    DBT_CMD = "cd /opt/airflow/dbt && dbt"
    DBT_FLAGS = "--profiles-dir . --no-partial-parse"

    ingest = BashOperator(
        task_id='kite_ingest',
        bash_command='USE_NEON=true python /opt/airflow/scripts/kite_ingest.py'
    )

    dbt_staging = BashOperator(
        task_id='dbt_staging',
        bash_command=f"""
            {NEON_ENV} {DBT_CMD} run --select staging {DBT_FLAGS}
        """
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command=f"{NEON_ENV} {DBT_CMD} test {DBT_FLAGS}"
    )

    dbt_marts = BashOperator(
        task_id='dbt_marts',
        bash_command=f"{NEON_ENV} {DBT_CMD} run --select marts {DBT_FLAGS}"
    )

    ingest >> dbt_staging >> dbt_test >> dbt_marts