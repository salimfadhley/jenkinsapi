#! /bin/bash
virtualenv venv --python=`which python3` --prompt="(jenkinsapi)" --clear
source venv/bin/activate
pip install --upgrade pip
pip install --upgrade wheel
