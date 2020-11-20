# Build tools - venv must be initialised beforehand

SHELL := /bin/bash
export PIPENV_VERBOSITY = -1
export PYVERSION=$(python -V)

.PHONY: check_virtualenv install test travis_test travis_mypy

test: travis_test
	python -m isort -c .
	# isort behaves differently under travis, so don't run it there
	python -m mypy --ignore-missing-imports --disallow-untyped-calls *.py

travis_test:
	python -m flake8 -v --exclude=.idea,.git,venv

travis_mypy:
	echo "PYVERSION '${PYVERSION}'"
	# Fails under py 3.9 - https://github.com/PyCQA/pylint/issues/3882
	if [ "${PYVERSION:7:3}" != "3.9" ]; then python -m pylint *.py; fi
	python -m mypy --ignore-missing-imports --disallow-untyped-calls *.py

check_virtualenv:
	pipenv --venv

install: check_virtualenv
	pipenv install

venv:
	python3 -m venv venv