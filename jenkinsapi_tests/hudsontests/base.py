import unittest
import jenkinsapi_tests.systests
from jenkinsapi_tests.systests.job_configs import EMPTY_JOB
from jenkinsapi.jenkins import Jenkins


class BaseSystemTest(unittest.TestCase):

    def setUp(self):
        port = jenkinsapi_tests.hudsontests.state['launcher'].http_port
        print "Hudson started"
        self.hudson = Jenkins('http://localhost:%d' % port, "admin", "admin")
        self._delete_all_jobs()
        self._delete_all_views()

    def tearDown(self):
        pass

    def _delete_all_jobs(self):
        self.hudson.poll()
        for name in self.hudson.get_jobs_list():
            self.hudson.delete_job(name)

    def _delete_all_views(self):
        all_view_names = self.hudson.views.keys()[1:]
        for name in all_view_names:
            del self.hudson.views[name]

    def _create_job(self, name='whatever', config=EMPTY_JOB):
        job = self.hudson.create_job(name, config)
        self.hudson.poll()
        return job

    def assertJobIsPresent(self, name):
        self.hudson.poll()
        self.assertTrue(name in self.hudson,
                        'Job %r is absent in Hudson.' % name)

    def assertJobIsAbsent(self, name):
        self.hudson.poll()
        self.assertTrue(name not in self.hudson,
                        'Job %r is present in Hudson.' % name)
