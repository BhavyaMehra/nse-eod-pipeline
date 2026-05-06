from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime
import pendulum

local_tz = pendulum.timezone('Asia/Kolkata')

default_args = {
    'owner': 'bhavya',
    'retries': 1
}

with DAG(
    dag_id='eod_pipeline',
    default_args=default_args,
    start_date=datetime(2026, 5, 1, tzinfo=local_tz),
    schedule='45 10 * * 1-5',
    catchup=False,
    tags=['nse', 'eod', 'pipeline'],
) as dag:
    
    ingest = BashOperator(
        task_id='kite_ingest',
        bash_command='python /opt/airflow/scripts/kite_ingest.py'
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/dbt && dbt run --profiles-dir /opt/airflow/dbt'
    )

    ingest >> dbt_run