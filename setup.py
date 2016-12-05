import os
from setuptools import setup

PROJECT_ROOT, _ = os.path.split(__file__)
REVISION = '0.3.4'
PROJECT_NAME = 'JenkinsAPI'
PROJECT_AUTHORS = 'Salim Fadhley, Aleksey Maksimov'
# Please see readme.rst for a complete list of contributors
PROJECT_EMAILS = 'salimfadhley@gmail.com, ctpeko3a@gmail.com'
PROJECT_URL = 'https://github.com/pycontribs/jenkinsapi'
SHORT_DESCRIPTION = (
    'A Python API for accessing resources on a Jenkins '
    'continuous-integration server.'
)

try:
    DESCRIPTION = open(os.path.join(PROJECT_ROOT, 'README.rst')).read()
except IOError:
    DESCRIPTION = SHORT_DESCRIPTION

GLOBAL_ENTRY_POINTS = {
    'console_scripts': [
        'jenkins_invoke=jenkinsapi.command_line.jenkins_invoke:main',
        'jenkinsapi_version=jenkinsapi.command_line.jenkinsapi_version:main'
    ]
}

install_requires = [
    'requests>=2.3.0',
    'pytz>=2014.4',
    'six>=1.10.0',
]

tests_require = [line.strip()
                 for line in open('requirements/dev-requirements.txt')
                 if line.strip()]

setup(
    name=PROJECT_NAME.lower(),
    version=REVISION,
    author=PROJECT_AUTHORS,
    author_email=PROJECT_EMAILS,
    packages=[
        'jenkinsapi',
        'jenkinsapi.utils',
        'jenkinsapi.command_line',
        'jenkinsapi_tests',
        'jenkinsapi_utils',
        ],
    zip_safe=True,
    include_package_data=False,
    install_requires=install_requires,
    test_suite='nose.collector',
    tests_require=tests_require,
    entry_points=GLOBAL_ENTRY_POINTS,
    url=PROJECT_URL,
    description=SHORT_DESCRIPTION,
    long_description=DESCRIPTION,
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Testing',
    ],
)
