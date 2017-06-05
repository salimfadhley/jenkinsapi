.PHONY: test lint tox coverage

test:
	python setup.py test

lint:
	pep8 --ignore=E501 jenkinsapi/*.py
	pylint --rcfile=./pylintrc jenkinsapi/*.py --disable R0912

tox:
	tox

coverage:
	python setup.py test
