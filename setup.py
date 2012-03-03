from setuptools import setup
import os

PROJECT_ROOT, _ = os.path.split(__file__)
DESCRIPTION = open(os.path.join(PROJECT_ROOT, "README.rst")).read()
VERSION = REVISION = '0.1.4'
PROJECT_NAME = 'JenkinsAPI'
PROJECT_AUTHORS = "Salim Fadhley, Ramon van Alteren, Ruslan Lutsenko"
PROJECT_EMAILS = 'salimfadhley@gmail.com, ramon@vanalteren.nl, ruslan.lutcenko@gmail.com'
PROJECT_URL = "https://github.com/salimfadhley/jenkinsapi"
SHORT_DESCRIPTION = 'A Python API for accessing resources on a Jenkins continuous-integration server.'

GLOBAL_ENTRY_POINTS = {
        "console_scripts": ["jenkins_invoke=jenkinsapi.command_line.jenkins_invoke:main"]
        }

# Actual setup

setup(name=PROJECT_NAME.lower(),
      version=VERSION,
      author=PROJECT_AUTHORS,
      author_email=PROJECT_EMAILS,
      packages=["jenkinsapi", 'jenkinsapi.utils', 'jenkinsapi.command_line'],
      zip_safe=True,
      include_package_data=False,
      entry_points=GLOBAL_ENTRY_POINTS,
      url=PROJECT_URL,
      description=SHORT_DESCRIPTION,
      long_description=DESCRIPTION,
      )
