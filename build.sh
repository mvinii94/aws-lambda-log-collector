#!/usr/bin/env bash

# activate venv
source ./venv/bin/activate

# build
python -m pip install --upgrade setuptools wheel twine
python setup.py sdist bdist_wheel

# upload
python -m pip install --upgrade twinepython -m pip install --upgrade twine
python -m twine upload dist/*

# clean
rm -rf __pycache__ dist aws_lambda_log_collector.egg-info build
