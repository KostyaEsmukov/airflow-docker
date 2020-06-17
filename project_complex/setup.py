#!/usr/bin/env python
import glob
from setuptools import setup

setup(data_files={"airflow/dags": glob.glob("dags/**.*")}.items())
