from pathlib import Path

import pytest
from project_common.testing_cli import *  # noqa

import project_simple


@pytest.fixture(scope="session")
def src_root_path():
    return Path(project_simple.__file__).parent
