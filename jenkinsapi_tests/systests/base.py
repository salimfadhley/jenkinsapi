# For tests on python 2.6 please use unittest2 library
try:
    import unittest2 as unittest
except ImportError:
    import unittest

import logging
import jenkinsapi_tests.systests
from jenkinsapi_tests.systests.job_configs import EMPTY_JOB
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.job import Job

log = logging.getLogger(__name__)

DEFAULT_JENKINS_PORT = 8080


class BaseSystemTest(unittest.TestCase):

    def setUp(self):
        try:
            port = jenkinsapi_tests.systests.state['launcher'].http_port
        except KeyError:
            log.warning(
                "Jenkins was not launched from the test-framework, "
                "assuming port %i" %
                DEFAULT_JENKINS_PORT)
            port = DEFAULT_JENKINS_PORT
        self.jenkins = Jenkins('http://localhost:%d' % port)
        self._delete_all_jobs()
        self._delete_all_views()
        self._delete_all_credentials()

    def tearDown(self):
        pass

    def _delete_all_jobs(self):
        self.jenkins.poll()
        for name in self.jenkins.keys():
            del self.jenkins[name]

    def _delete_all_views(self):
        all_view_names = self.jenkins.views.keys()[1:]
        for name in all_view_names:
            del self.jenkins.views[name]

    def _delete_all_credentials(self):
        all_cred_names = self.jenkins.credentials.keys()
        for name in all_cred_names:
            del self.jenkins.credentials[name]

    def _create_job(self, name='whatever', config=EMPTY_JOB):
        job = self.jenkins.create_job(name, config)
        self.jenkins.poll()
        return job

    def assertJobIsPresent(self, name):
        self.jenkins.poll()
        self.assertTrue(name in self.jenkins,
                        'Job %r is absent in jenkins.' % name)
        self.assertIsInstance(self.jenkins.get_job(name), Job)
        self.assertIsInstance(self.jenkins[name], Job)

    def assertJobIsAbsent(self, name):
        self.jenkins.poll()
        self.assertTrue(name not in self.jenkins,
                        'Job %r is present in jenkins.' % name)
