from datetime import datetime
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
import requests

with DAG(dag_id = 'ingestion',
         start_date=datetime(2022, 1, 1),
         schedule="0 0 * * *"
         ) as dag:
    # Tasks are represented as operators

    def extract(**kwargs):
        req_extract = requests.get(url = 'https://randomuser.me/api/')
        print(req_extract.json())

    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract,
    )

    extract_task