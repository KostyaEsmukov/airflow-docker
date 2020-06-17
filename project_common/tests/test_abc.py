from contextlib import ExitStack
from typing import Any
from unittest.mock import patch

import click
import pendulum
import pytest
from airflow import DAG, configuration, macros
from click.testing import CliRunner

import project_common.abc
from project_common.abc import AirflowContext, AirflowTask, create_cli


class DummyTask(AirflowTask):
    def execute(self):
        pass


@pytest.fixture
def airflow_context():
    return {
        "dag": DAG("test-dag"),
        "next_ds": "2018-10-28",
        "prev_ds": "2018-10-28",
        "ds_nodash": "20181028",
        "ts": "2018-10-28T16:24:36.908747+00:00",
        "ts_nodash": "20181028T162436.908747+0000",
        "yesterday_ds": "2018-10-27",
        "yesterday_ds_nodash": "20181027",
        "tomorrow_ds": "2018-10-29",
        "tomorrow_ds_nodash": "20181029",
        "END_DATE": "2018-10-28",
        "end_date": "2018-10-28",
        # 'dag_run': <DagRun synctogit-next @ 2018-10-28 16:24:36.908747+00:00: scheduled__2018-10-28T16:24:36.908747+00:00, externally triggered: False>,  # noqa
        "run_id": "scheduled__2018-10-28T16:24:36.908747+00:00",
        "execution_date": pendulum.datetime(2018, 10, 28, 16, 24, 36),
        "prev_execution_date": pendulum.datetime(2018, 10, 28, 15, 54, 36),
        "next_execution_date": pendulum.datetime(2018, 10, 28, 16, 54, 36),
        "latest_date": "2018-10-28",
        "macros": macros,
        "params": {},
        "tables": None,
        # 'task': <Task(PythonOperator): evernote>,
        # 'task_instance': <TaskInstance: synctogit-next.evernote 2018-10-28T16:24:36.908747+00:00 [running]>,  # noqa
        # 'ti': <TaskInstance: synctogit-next.evernote 2018-10-28T16:24:36.908747+00:00 [running]>,  # noqa
        "task_instance_key_str": "synctogit-next__evernote__20181028",
        "conf": configuration,
        "test_mode": False,
        "var": {"value": None, "json": None},
        "inlets": [],
        "outlets": [],
        "templates_dict": None,
    }


def test_run_task(airflow_context):
    t = DummyTask(airflow_context)
    assert t.context.execution_date
    assert isinstance(t.context, AirflowContext)
    t()


def test_click_defaults():
    cli = create_cli()

    @cli.register_callback
    class DummyTask(AirflowTask):
        @click.option("--some", type=int)
        def __init__(self, context: Any, some: int = 42) -> None:
            super().__init__(context)
            self.some = some

        def execute(self):
            print(self.some)

    runner = CliRunner()
    with ExitStack() as stack:
        stack.enter_context(patch.object(project_common.abc, "logging"))
        stack.enter_context(patch.object(project_common.abc, "logger"))
        result = runner.invoke(cli._main, ["--execution_date=2018-10-20", "DummyTask"])
        assert result.exit_code == 0
        assert result.output.strip() == "42"
