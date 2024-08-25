from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

DAG(
    dag_id = 'ingestion',
    schedule= '* * * 5',
)