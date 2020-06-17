import datetime
import logging
import random
from time import sleep
from typing import Any

import click

from project_common.abc import AirflowTask, create_cli
from project_common.cli_types import type_timedelta

logger = logging.getLogger(__name__)
cli = create_cli()


@cli.register_callback
class RandomFailTask(AirflowTask):
    @click.option("--probability", type=float, required=True)
    @click.option("--sleep_interval", type=str, callback=type_timedelta)
    def __init__(
        self, context: Any, probability: float, sleep_interval: datetime.timedelta
    ) -> None:
        super().__init__(context)
        self.probability = probability
        self.sleep_interval = sleep_interval

    def execute(self) -> None:
        logger.info("Sleeping %s seconds", self.sleep_interval)
        sleep(self.sleep_interval.total_seconds())

        should_fail = random.random() < self.probability
        if should_fail:
            raise RuntimeError("dummy error")


cli.maybe_run(__name__)
