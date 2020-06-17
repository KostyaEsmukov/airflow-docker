FROM apache/airflow:1.10.10

USER root

RUN pip install 'airflow-declarative==1.1'


# XXX declarative patch
# XXX airflow_pull_dags_folder.py

USER airflow
