import importlib
import inspect
import os.path
import re
from pathlib import Path

import pytest

from project_common.abc import AirflowTask, Cli


@pytest.fixture(scope="session")
def import_all_modules(src_root_path: Path):
    root = src_root_path
    py_files = [py_file.relative_to(root.parent) for py_file in root.glob("**/*.py")]
    modules = [str(py_file).replace(os.path.sep, ".") for py_file in py_files]
    modules = [re.sub(r"(\.__init__\.py|\.py)$", "", module) for module in modules]
    for module in modules:
        importlib.import_module(module)


@pytest.fixture(scope="session")
def all_airflow_tasks(import_all_modules):
    def dfs(task):
        ll = (
            dfs(cls)
            + (
                [cls]
                # Ensure that the class is not abstract, see PEP3119:
                if not cls.__abstractmethods__  # type: ignore
                else []
            )
            for cls in task.__subclasses__()
            if not cls.__module__.startswith("test")
        )
        return [task for tasks in ll for task in tasks]

    return dfs(AirflowTask)


@pytest.fixture(scope="session")
def all_modules_with_tasks(all_airflow_tasks):
    modules = {task.__module__ for task in all_airflow_tasks}
    return [importlib.import_module(module) for module in modules]


def test_all_modules_have_cli(all_modules_with_tasks):
    for module in all_modules_with_tasks:
        assert Cli is type(getattr(module, "cli", None)), module.__name__  # noqa


def test_all_modules_have_cli_maybe_run(all_modules_with_tasks):
    for module in all_modules_with_tasks:
        source = inspect.getsource(module)
        assert source.strip().endswith("\ncli.maybe_run(__name__)"), module.__name__


def test_all_tasks_have_cli_register_callback_decorator(all_airflow_tasks):
    for task_cls in all_airflow_tasks:
        assert (
            getattr(task_cls, "_airflow_docker_cli_registered_callback", None) is True
        ), task_cls.__name__


def test_all_init_args_have_click_option(all_airflow_tasks):
    for task_cls in all_airflow_tasks:
        sig = inspect.signature(task_cls.__init__)
        for parameter in sig.parameters.values():
            assert parameter.kind not in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ), "*args and **kwargs parameters are disallowed in callbacks __init__"

        defined_param_names = list(sig.parameters.keys())
        assert defined_param_names[0] == "self", task_cls.__name__
        assert defined_param_names[1] == "context", task_cls.__name__

        defined_custom_param_names = defined_param_names[2:]
        defined_click_option_names = [
            option.name for option in getattr(task_cls.__init__, "__click_params__", [])
        ]

        assert set(defined_custom_param_names) == set(
            defined_click_option_names
        ), task_cls.__name__
        # TODO also check:
        # type annotations vs option.type
        # default vs required=True
        # option.default should be missing
