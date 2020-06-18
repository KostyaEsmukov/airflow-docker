import datetime

from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

args = {
    "catchup": False,
    "owner": "Airflow",
    "start_date": days_ago(2),
}

dag = DAG(
    dag_id="project_complex_pymath",
    default_args=args,
    schedule_interval=datetime.timedelta(minutes=1),
    tags=["project_complex", "python_dag"],
)


def multiply(a, b):
    print(a * b)


PythonOperator(
    task_id="multiply",
    python_callable=multiply,
    op_kwargs={"a": 5, "b": 10},
    dag=dag,
)
