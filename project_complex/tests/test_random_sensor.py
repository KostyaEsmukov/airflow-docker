import pendulum
import pytest
from project_common.abc import AirflowContext

from project_complex.random_sensor import RandomSensor


@pytest.fixture
def context():
    return AirflowContext(
        execution_date=pendulum.datetime(2018, 10, 10, 13, 38, 56, 0, "Europe/Moscow")
    )


def test_random_sensor(context):
    assert not RandomSensor(context, probability=0.0).poke()
    assert RandomSensor(context, probability=1.0).poke()
