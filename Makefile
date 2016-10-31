.PHONY: test lint tox coverage

test:
	py.test -sv jenkinsapi_tests

lint:
	pep8 --ignore=E501 jenkinsapi/*.py
	pylint --rcfile=pylintrc jenkinsapi/*.py --disable R0912

tox:
	tox

coverage:
	py.test -sv --cov=jenkinsapi --cov-report=term-missing --cov-report=xml jenkinsapi_tests
