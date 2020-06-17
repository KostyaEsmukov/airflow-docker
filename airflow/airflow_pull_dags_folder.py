#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

dags_path = Path("/var/my_airflow/airflow/dags/dags_folder")
group = "airflow"  # "ansible_admin"


def ensure_no_dirs(p):
    dirs = [x for x in p.iterdir() if x.is_dir()]
    if dirs:
        raise RuntimeError(f"Found unexpected dirs {dirs} at {p}")


def hash_image(image):
    image_name = image.split(":")[0]
    *_, user, name = image_name.split("/")
    return f"{user}_{name}"


def main(image):
    dest_gen = dags_path / hash_image(image)
    dest_gen.mkdir(exist_ok=True)
    shutil.chown(dest_gen, group=group)
    os.chmod(dest_gen, 0o775)

    ensure_no_dirs(dest_gen)
    current_dags = {x.name for x in dest_gen.iterdir() if x.is_file()}

    with tempfile.TemporaryDirectory() as tempdir:
        dest = Path(tempdir).resolve() / "gen"
        dest.mkdir()

        subprocess.check_call(
            f"docker run --rm {image} pipe_dags | tar x --no-same-owner",
            shell=True,
            cwd=dest,
        )

        ensure_no_dirs(dest)
        next_dags = {x.name for x in dest.iterdir() if x.is_file()}

        delete_dags = current_dags - next_dags
        # TODO don't use filesystem, compute everything in-memory using tar in python
        for f in next_dags:
            shutil.chown(dest / f, group=group)
            os.chmod(dest / f, 0o664)
            shutil.copy2(dest / f, dest_gen / f)
            shutil.chown(dest_gen / f, group=group)
        for f in delete_dags:
            (dest_gen / f).unlink()


if __name__ == "__main__":
    image = sys.argv[1]
    main(image)
