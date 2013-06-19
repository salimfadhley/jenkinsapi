============
jenkinsapi
============

About this library
-------------------

Jenkins is the market leading continuous integration system, originally created by Kohsuke Kawaguchi.

Jenkins (and It's predecessor Hudson) are useful projects for automating common development tasks (e.g. unit-testing, production batches) - but they are somewhat Java-centric. Thankfully the designers have provided an excellent and complete REST interface. This library wraps up that interface as more conventional python objects in order to make many Jenkins oriented tasks easier to automate.

This library can help you:

 * Query the test-results of a completed build
 * Get a objects representing the latest builds of a job
 * Search for artefacts by simple criteria
 * Block until jobs are complete
 * Install artefacts to custom-specified directory structures
 * username/password auth support for jenkins instances with auth turned on
 * Ability to search for builds by subversion revision
 * Ability to add/remove/query Jenkins slaves
 * Ability to add/remove/modify Jenkins views

Known bugs
----------
 [ ] Currently incompatible with Jenkins > 1.518. Job deletion operations fail unless Cross-Site scripting protection is disabled.

 For other issues, please refer to the support URL below.

Important Links
---------------

Support & bug-reportst: https://github.com/salimfadhley/jenkinsapi/issues?direction=desc&sort=comments&state=open

Project source code: github: https://github.com/salimfadhley/jenkinsapi

Project documentation: https://jenkinsapi.readthedocs.org/en/latest/

Releases: http://pypi.python.org/pypi/jenkinsapi

Installation
-------------

Egg-files for this project are hosted on PyPi. Most Python users should be able to use pip or setuptools to automatically install this project.

Most users can do the following:
::
    pip install jenkinsapi

Or..
::
    easy_install jenkinsapi

Example
-------

JenkinsAPI is intended to map the objects in Jenkins (e.g. Builds, Views, Jobs) into easily managed Python objects::

	Python 2.7.4 (default, Apr 19 2013, 18:28:01)
	[GCC 4.7.3] on linux2
	Type "help", "copyright", "credits" or "license" for more information.
	>>> import jenkinsapi
	>>> from jenkinsapi.jenkins import Jenkins
	>>> J = Jenkins('http://localhost:8080')
	>>> J.keys() # Jenkins objects appear to be dict-like, mapping keys (job-names) to
	['foo', 'test_jenkinsapi']
	>>> J['test_jenkinsapi']
	<jenkinsapi.job.Job test_jenkinsapi>
	>>> J['test_jenkinsapi'].get_last_good_build()
	<jenkinsapi.build.Build test_jenkinsapi #77>

Project Authors
----------------

 * Salim Fadhley (sal@stodge.org)
 * Ramon van Alteren (ramon@vanalteren.nl)
 * Ruslan Lutsenko (ruslan.lutcenko@gmail.com)
 * Cleber J Santos (cleber@simplesconsultoria.com.br)
 * William Zhang (jollychang@douban.com)
 * Victor Garcia (bravejolie@gmail.com)
 * Bradley Harris (bradley@ninelb.com)
 * Aleksey Maksimov (ctpeko3a@gmail.com)

License
--------

The MIT License (MIT): Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
