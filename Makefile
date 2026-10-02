.PHONY: lint test typecheck build validate-contract test-contract test-bdd test-mock test-all

lint:
	python scripts/agileaidev_gate.py lint

test:
	python scripts/agileaidev_gate.py test

typecheck:
	python scripts/agileaidev_gate.py typecheck

build:
	python scripts/agileaidev_gate.py build

validate-contract:
	python scripts/agileaidev_gate.py validate-contract

test-contract:
	python scripts/agileaidev_gate.py test-contract

test-bdd:
	python scripts/agileaidev_gate.py test-bdd

test-mock:
	python scripts/agileaidev_gate.py test-mock

test-all:
	python scripts/agileaidev_gate.py lint test typecheck build validate-contract test-contract test-bdd test-mock
