import logging
import random
from typing import Any

import click

from project_common.abc import AirflowPokeSensorTask, create_cli

logger = logging.getLogger(__name__)
cli = create_cli()


@cli.register_callback
class RandomSensor(AirflowPokeSensorTask):
    @click.option("--probability", type=float, required=True)
    @click.option("--poke_interval", type=float)
    @click.option("--timeout", type=float)
    def __init__(
        self,
        context: Any,
        *,
        poke_interval: float = 60,
        timeout: float = 60 * 60 * 24 * 7,
        probability: float
    ) -> None:
        super().__init__(context, poke_interval=poke_interval, timeout=timeout)
        self.probability = probability

    def poke(self) -> bool:
        if random.random() < self.probability:
            return True
        else:
            return False


cli.maybe_run(__name__)
