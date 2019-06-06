SHELL := /bin/bash
check: lint test

lint:
	source bin/activate && flake8 waddle
	source bin/activate && flake8 tests
	source bin/activate && pylint --rcfile waddle.pylintrc waddle
	source bin/activate && pylint --rcfile tests.pylintrc tests

test:
	source bin/activate \
	  && python -B -O -m pytest \
		   --durations 10 \
		   --cov waddle --cov-report term-missing tests/

setup: venv requirements

venv:
	if which python3.7 && [ ! -d bin ] ; then python3.7 -m venv . ; fi
	if which python3.6 && [ ! -d bin ] ; then python3.6 -m venv . ; fi

requirements:
	source bin/activate \
	  && python -m pip install -q -U pip \
	  && pip install -q -r requirements.txt

clean-venv:
	if [ -d bin ] ; then rm -R bin ; fi
	if [ -d lib ] ; then rm -R lib ; fi

build:
	source bin/activate \
	  && python -B -O setup.py sdist \
	  && python -B -O setup.py bdist_wheel

bumpversion:
	source bin/activate \
	  && bumpversion minor

clean:
	source bin/activate \
	  && python -B -O setup.py clean
	rm -rf build dist

upload:
	source bin/activate \
	  && twine upload dist/*

deploy: bumpversion clean build upload
