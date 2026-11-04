import os
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

HOME = os.environ.get("DALILI_HOME", "/opt/dalili")

with DAG(
    dag_id="dalili_pipeline",
    start_date=datetime(2026, 11, 1),
    schedule="@daily",
    catchup=False,
) as dag:
    collect = BashOperator(
        task_id="collect",
        bash_command=f"python {HOME}/collect/main.py",
    )
    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=f"cd {HOME}/transformation/dbt && dbt build --profiles-dir .",
    )
    collect >> dbt_build
