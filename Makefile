
check: lint test coverage

lint:
	flake8 stork
	flake8 tests
	pylint --rcfile stork.pylintrc stork
	pylint --rcfile tests.pylintrc tests

test:
	python -B -O -m pytest tests

coverage:
	python -B -O -m pytest --cov stork --cov-report term-missing tests/
