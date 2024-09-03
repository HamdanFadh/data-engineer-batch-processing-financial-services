from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests
import csv

# Define the DAG
ingestion_dag = DAG(
    dag_id='1__ingestion',
    start_date=datetime(2024, 9, 3, 11, 49),  # Set to UTC time
    schedule_interval="*/10 * * * *",  # Run every 10 minutes
    catchup=False  # Avoid backfilling
)

def extract(**kwargs):
    req_extract = requests.get(url='https://randomuser.me/api/')
    req_extract = req_extract.json()
    res = req_extract['results'][0]
    # Push data to XCom
    kwargs['ti'].xcom_push(key='extracted_data', value=res)

def transform(**kwargs):
    # Pull data from XCom
    res = kwargs['ti'].xcom_pull(key='extracted_data', task_ids='extract')
    data = {
        'id': res['login']['username'],
        'first_name': res['name']['first'],
        'last_name': res['name']['last'],
        'gender': res['gender'],
        'email': res['email'],
        'phone': res['phone']
    }
    # Push transformed data to XCom
    kwargs['ti'].xcom_push(key='transformed_data', value=data)

def export(**kwargs):
    # Pull data from XCom
    data = kwargs['ti'].xcom_pull(key='transformed_data', task_ids='transform')
    with open('customer.csv', 'a', newline='') as csvfile:
        field = ['id', 'first_name', 'last_name', 'gender', 'email', 'phone']
        writer = csv.DictWriter(csvfile, fieldnames=field)
        writer.writerow(data)

# Define the tasks
extract_task = PythonOperator(
    task_id="extract",
    python_callable=extract,
    provide_context=True,
    dag=ingestion_dag
)

transform_task = PythonOperator(
    task_id="transform",
    python_callable=transform,
    provide_context=True,
    dag=ingestion_dag
)

export_task = PythonOperator(
    task_id="export",
    python_callable=export,
    provide_context=True,
    dag=ingestion_dag
)

# Set task dependencies
extract_task >> transform_task >> export_task
