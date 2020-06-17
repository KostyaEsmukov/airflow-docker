from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

args = {
    "owner": "Airflow",
    "start_date": days_ago(2),
}

dag = DAG(
    dag_id="project_complex_pymath",
    default_args=args,
    schedule_interval=None,
    tags=["project_complex", "python_dag"],
)


def multiply(ds, a, b):
    print(ds)
    print(a * b)


PythonOperator(
    task_id="multiply",
    provide_context=True,
    python_callable=multiply,
    op_kwargs={"a": 5, "b": 10},
    dag=dag,
)
