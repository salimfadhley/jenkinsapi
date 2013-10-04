#! /bin/bash
if ! command -v virtualenv >/dev/null 2>&1; then
    echo "You should install virtualenv, check http://www.virtualenv.org/"
    exit 1
fi
virtualenv .
source bin/activate
python setup.py develop
easy_install nose
easy_install mock
easy_install requests
easy_install coverage
test -z "$WORKSPACE" && WORKSPACE="`pwd`"
nosetests jenkinsapi_tests --with-xunit --with-coverage --cover-html --cover-html-dir="$WORKSPACE/coverage_report" --cover-package=jenkinsapi --verbose
