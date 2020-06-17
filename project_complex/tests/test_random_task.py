import datetime

import pendulum
import pytest
from project_common.abc import AirflowContext

from project_complex.random_task import RandomFailTask


@pytest.fixture
def context():
    return AirflowContext(
        execution_date=pendulum.datetime(2018, 10, 10, 13, 38, 56, 0, "Europe/Moscow")
    )


def test_random_task_success(context):
    task = RandomFailTask(
        context, probability=0.0, sleep_interval=datetime.timedelta(0)
    )
    task.execute()


def test_random_task_fail(context):
    task = RandomFailTask(
        context, probability=1.0, sleep_interval=datetime.timedelta(0)
    )
    with pytest.raises(RuntimeError):
        task.execute()
