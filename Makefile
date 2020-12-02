# Build tools - venv must be initialised beforehand

SHELL := /bin/bash
export PIPENV_VERBOSITY = -1

.PHONY: check_virtualenv install test travis_test travis_lint

test: travis_safe_tests
	python -m isort -c .
	# isort behaves differently under travis, so don't run it there

travis_safe_tests:
	python -m flake8 -v *.py
	python -m mypy --ignore-missing-imports --disallow-untyped-calls *.py
	# Fails under py 3.9 - https://github.com/PyCQA/pylint/issues/3882
	if [ "${TRAVIS_PYTHON_VERSION}" != "3.9" ]; then python -m pylint *.py; fi

check_virtualenv:
	pipenv --venv

install: check_virtualenv
	pipenv install

venv:
	python3 -m venv venv