import pendulum
import pytest

from project_common.abc import AirflowContext

from project_simple.echo import EchoTask


@pytest.fixture
def context():
    return AirflowContext(
        execution_date=pendulum.datetime(2018, 10, 10, 13, 38, 56, 0, "Europe/Moscow")
    )


def test_echo_task(context, caplog):
    task = EchoTask(context, i1=3, i2=5)
    task.execute()
    assert "Result: 8" in caplog.text
