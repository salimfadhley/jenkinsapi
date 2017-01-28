CSRF Protection
===============
Jenkins servers which have the `CSRF protection <https://wiki.jenkins-ci.org/display/JENKINS/CSRF+Protection>`_ enabled need to be started differently to use the ``CrumbRequester`` class that adds a special crumb field in the requests headers.

::

    from jenkinsapi.jenkins import Jenkins
    from jenkinsapi.utils.crumb_requester import CrumbRequester

    jenkins_url = 'http://jenkins_host:8080'
    crumb_requester = CrumbRequester(baseurl=jenkins_url, username='foouser', password='foopassword')
    crumbed_server = Jenkins(jenkins_url, username='foouser', password='foopassword', requester=crumb_requester)


The ``CrumbRequester`` will take care of retrieving the crumb automatically for you for all requests made with the library.


