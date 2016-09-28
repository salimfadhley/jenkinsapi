.PHONY: test lint tox coverage

test:
	nosetests -sv jenkinsapi_tests

lint:
	pep8 --ignore=E501 jenkinsapi/*.py
	pylint --rcfile=pylintrc jenkinsapi/*.py --disable R0912

tox:
	tox

coverage:
	nosetests -v --with-coverage --cover-xml jenkinsapi_tests
