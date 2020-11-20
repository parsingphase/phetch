# Build tools - venv must be initialised beforehand

SHELL := /bin/bash
export PIPENV_VERBOSITY = -1

.PHONY: check_virtualenv install test travis_test

test: travis_test
	python -m isort -c .
	# isort behaves differently under travis, so don't run it there

travis_test:
	python -m flake8 -v --exclude=.idea,.git,venv
	python -m pylint *.py
	python -m mypy --ignore-missing-imports --disallow-untyped-calls *.py

check_virtualenv:
	pipenv --venv

install: check_virtualenv
	pipenv install

venv:
	python3 -m venv venv