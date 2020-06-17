import abc
import collections.abc
import inspect
import logging
import time
from typing import Any, Mapping, NamedTuple, Optional, Union

import click
import pendulum
from pkg_resources import get_distribution

logger = logging.getLogger(__name__)


class Cli:
    def __init__(self, click_main):
        self._main = click_main
        self._pass_airflow_context = click.make_pass_decorator(AirflowContext)

    @classmethod
    def create(cls, package: Optional[str]):
        if package:
            pkg = get_distribution(package)
            version = pkg.version
        else:
            version = "UNKNOWN"

        @click.group()
        @click.option("--loglevel", default="info")
        @click.option("--execution_date", type=str, required=True)
        @click.version_option(version=version)
        @click.pass_context
        def main(ctx, *, loglevel, execution_date):
            logging.basicConfig(level=getattr(logging, loglevel.upper()))
            if package:
                logger.info("%s version: %s", package, version)
            context = AirflowContext(
                execution_date=pendulum.parse(execution_date, exact=True)
            )
            ctx.obj = context

        return cls(main)

    def register_callback(self, cls: "AirflowTask"):
        name = cls.__name__  # type: ignore

        @self._pass_airflow_context
        def cmd(context, **kwargs):
            cls(context, **kwargs)()

        assert not getattr(cmd, "__click_params__", None)
        if getattr(cls.__init__, "__click_params__", None) is not None:  # type: ignore
            cmd.__click_params__ = cls.__init__.__click_params__  # type: ignore
            sig = inspect.signature(cls.__init__)  # type: ignore
            defaults = {
                name: parameter.default
                for name, parameter in sig.parameters.items()
                if parameter.default is not inspect.Parameter.empty
            }
            for click_option in cmd.__click_params__:
                assert click_option.default is None, (
                    "click option should not have a default value. "
                    "Specify it in the function signature"
                )
                click_option.default = defaults.get(click_option.name)

        cmd = self._main.command(name=name)(cmd)

        # Sensed in tests as a way to find out if an Airflow Task
        # has been wrapped with this callback:
        cls._airflow_docker_cli_registered_callback = True  # type: ignore

        return cls

    def maybe_run(self, name):
        if name == "__main__":
            self._main()


def create_cli():
    caller_frame = inspect.stack()[1]
    caller_module = inspect.getmodule(caller_frame[0])
    caller_package = caller_module.__package__ or None
    return Cli.create(caller_package)


class AirflowContext(NamedTuple):
    execution_date: pendulum.datetime

    # dag_run: DagRun
    # dag: DAG
    # task: Task
    # task_instance: TaskInstance

    @classmethod
    def from_dict(cls, context):
        d = {k: context[k] for k in cls._fields}
        return cls(d)


class AirflowTask(abc.ABC):
    def __init__(self, context: Union[AirflowContext, Mapping[str, Any]]) -> None:
        if isinstance(context, AirflowContext):
            airflow_context = context
        elif isinstance(context, collections.abc.Mapping):
            airflow_context = AirflowContext.from_dict(context)
        else:
            raise ValueError(
                "context must be an instance of either a dict or an AirflowContext"
            )
        self.context: AirflowContext = airflow_context

    def __call__(self):
        return self.execute()

    @abc.abstractmethod
    def execute(self):
        pass


class AirflowPokeSensorTask(AirflowTask):
    # Reimplementation of BaseSensorOperator for Docker with mode=poke.
    #
    # reschedule mode is not implemented, because there's no way
    # to tell Airflow to reschedule or skip from within a Docker container.

    def __init__(
        self,
        context: Union[AirflowContext, Mapping[str, Any]],
        *,
        poke_interval: float = 60,
        timeout: float = 60 * 60 * 24 * 7,
    ) -> None:
        super().__init__(context)
        self.poke_interval = poke_interval
        self.timeout = timeout
        self._validate_input_values()

    def _validate_input_values(self) -> None:
        if not isinstance(self.poke_interval, (int, float)) or self.poke_interval < 0:
            raise RuntimeError("The poke_interval must be a non-negative number")
        if not isinstance(self.timeout, (int, float)) or self.timeout < 0:
            raise RuntimeError("The timeout must be a non-negative number")

    @abc.abstractmethod
    def poke(self) -> bool:
        pass

    def execute(self) -> None:
        started_at = time.monotonic()

        while not self.poke():
            if (time.monotonic() - started_at) > self.timeout:
                raise RuntimeError("Snap. Time is OUT.")
            time.sleep(self.poke_interval)
        logger.info("Success criteria met. Exiting.")
