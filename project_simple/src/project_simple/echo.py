import logging
from typing import Any

import click

from project_common.abc import AirflowTask, create_cli

logger = logging.getLogger(__name__)
cli = create_cli()


@cli.register_callback
class EchoTask(AirflowTask):
    @click.option("--i1", type=int, required=True)
    @click.option("--i2", type=int, required=True)
    @click.option("--i3", type=int)
    def __init__(self, context: Any, i1: int, i2, i3: int = 0) -> None:
        super().__init__(context)
        self.i = [i1, i2, i3]

    def execute(self) -> None:
        logger.info("Computing a sum of %r", self.i)
        s = sum(self.i)
        logger.info("Result: %s", s)


cli.maybe_run(__name__)
