from pathlib import Path

import airflow_declarative
import pytest
from airflow import DAG

DAG_DIR = Path("dags")
DAGS = list(DAG_DIR.glob("*.yml"))


@pytest.mark.parametrize("dag_path", DAGS, ids=[p.name for p in DAGS])
def test_load_airflow_dags(dag_path):
    dags = airflow_declarative.from_path(dag_path)
    assert all(isinstance(dag, DAG) for dag in dags)
