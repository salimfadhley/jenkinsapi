.PHONY: test lint tox coverage dist

test:
	py.test -sv --force-flaky jenkinsapi_tests

lint:
	pycodestyle
	pylint jenkinsapi/*.py

tox:
	tox

dist:
	python setup.py sdist bdist_wheel

coverage:
	py.test -sv --force-flaky --cov=jenkinsapi --cov-report=term-missing --cov-report=xml jenkinsapi_tests
