jenkinsapi
==========

.. image:: https://badge.fury.io/py/jenkinsapi.png
    :target: http://badge.fury.io/py/jenkinsapi

.. image:: https://travis-ci.org/salimfadhley/jenkinsapi.png?branch=master
        :target: https://travis-ci.org/salimfadhley/jenkinsapi

.. image:: https://landscape.io/github/salimfadhley/jenkinsapi/master/landscape.png
        :target: https://landscape.io/github/salimfadhley/jenkinsapi

.. image:: https://requires.io/github/salimfadhley/jenkinsapi/requirements.png?branch=master
        :target: https://requires.io/github/salimfadhley/jenkinsapi/requirements/?branch=master
        :alt: Requirements Status

About this library
-------------------

Jenkins is the market leading continuous integration system, originally created by Kohsuke Kawaguchi.

Jenkins (and It's predecessor Hudson) are useful projects for automating common development tasks (e.g. unit-testing, production batches) - but they are somewhat Java-centric. Thankfully the designers have provided an excellent and complete REST interface. This library wraps up that interface as more conventional python objects in order to make many Jenkins oriented tasks easier to automate.

This library allows you to automate most common Jenkins operations using Python.

* Ability to add/remove/query Jenkins jobs
* Ability to execute jobs and:
    * Query the results of a completed build
    * Block until jobs are complete or run jobs asyncronously
    * Get objects representing the latest builds of a job
* Work with build artefacts:
    * Search for artefacts by simple criteria
    * Install artefacts to custom-specified directory structures
* Ability to search for builds by source code revision
* Ability to add/remove/query:
    * Slaves (Webstart and SSH slaves)
    * Views (including nested views using NestedViews Jenkins plugin)
    * Credentials (username/password and ssh key)
* Username/password auth support for jenkins instances with auth turned on
* Ability to script jenkins installation including plugins

Python versions
---------------

The project have been tested and working on Python 2.7, 3.3 and 3.4.
It was tested previously on Python 2.6, so it may work on this version too.

Jenkins versions
----------------

Project tested on both stable (LTS) and latest Jenkins versions.

Known issues
------------
* Job deletion operations fail unless Cross-Site scripting protection is disabled.

For other issues, please refer to the support URL below.

Important Links
---------------

Support and bug-reports: https://github.com/salimfadhley/jenkinsapi/issues?direction=desc&sort=comments&state=open

Project source code: github: https://github.com/salimfadhley/jenkinsapi

Project documentation: https://jenkinsapi.readthedocs.org/en/latest/

Releases: http://pypi.python.org/pypi/jenkinsapi

Installation
-------------

Egg-files for this project are hosted on PyPi. Most Python users should be able to use pip or setuptools to automatically install this project.

Using Pip or Setuptools
^^^^^^^^^^^^^^^^^^^^^^^

Most users can do the following:

.. code-block:: bash

	pip install jenkinsapi

Or:

.. code-block:: bash

	easy_install jenkinsapi

Both of these techniques can be combined with virtualenv to create an application-specific installation.

Using your operating-system's package manager
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ubuntu users can now use apt to install this package:

.. code-block:: bash

    apt-get install python-jenkinsapi

Beware that this technique will get a somewhat older version of Jenkinsapi.

Example
-------

JenkinsAPI is intended to map the objects in Jenkins (e.g. Builds, Views, Jobs) into easily managed Python objects:

.. code-block:: python

	>>> import jenkinsapi
	>>> from jenkinsapi.jenkins import Jenkins
	>>> J = Jenkins('http://localhost:8080')
	>>> J.version
	1.542
	>>> J.keys() # Jenkins objects appear to be dict-like, mapping keys (job-names) to
	['foo', 'test_jenkinsapi']
	>>> J['test_jenkinsapi']
	<jenkinsapi.job.Job test_jenkinsapi>
	>>> J['test_jenkinsapi'].get_last_good_build()
	<jenkinsapi.build.Build test_jenkinsapi #77>
	...

More examples available on Github: https://github.com/salimfadhley/jenkinsapi/tree/master/examples

Testing
-------

If you have installed the test dependencies on your system already, you can run
the testsuite with the following command:

.. code-block:: bash

        python setup.py test

Otherwise using a virtualenv is recommended. Setuptools will automatically fetch
missing test dependencies:

.. code-block:: bash

        virtualenv
        source .venv/bin/active
        (venv) python setup.py test

Project Contributors
--------------------

* Salim Fadhley (sal@stodge.org)
* Aleksey Maksimov (ctpeko3a@gmail.com)
* Ramon van Alteren (ramon@vanalteren.nl)
* Ruslan Lutsenko (ruslan.lutcenko@gmail.com)
* Cleber J Santos (cleber@simplesconsultoria.com.br)
* William Zhang (jollychang@douban.com)
* Victor Garcia (bravejolie@gmail.com)
* Bradley Harris (bradley@ninelb.com)
* Kyle Rockman (kyle.rockman@mac.com)
* Sascha Peilicke (saschpe@gmx.de)
* David Johansen (david@makewhat.is)

Please do not contact these contributors directly for support questions! Use the GitHub tracker instead.

License
--------

The MIT License (MIT): Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
