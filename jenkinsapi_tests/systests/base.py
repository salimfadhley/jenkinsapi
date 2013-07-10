import unittest
from jenkinsapi_tests.systests.job_configs import EMPTY_JOB
from jenkinsapi.jenkins import Jenkins


class BaseSystemTest(unittest.TestCase):

    def setUp(self):
        self.jenkins = Jenkins('http://localhost:8080')
        self._delete_all_jobs()
        self._delete_all_views()

    def tearDown(self):
        pass

    def _delete_all_jobs(self):
        self.jenkins.poll()
        for name in self.jenkins.get_jobs_list():
            self.jenkins.delete_job(name)

    def _delete_all_views(self):
        all_view_names = self.jenkins.views.keys()[1:]
        for name in all_view_names:
            del self.jenkins.views[name]

    def _create_job(self, name='whatever', config=EMPTY_JOB):
        job = self.jenkins.create_job(name, config)
        self.jenkins.poll()
        return job

    def assertJobIsPresent(self, name):
        self.jenkins.poll()
        self.assertTrue(name in self.jenkins,
                        'Job %r is absent in jenkins.' % name)

    def assertJobIsAbsent(self, name):
        self.jenkins.poll()
        self.assertTrue(name not in self.jenkins,
                        'Job %r is present in jenkins.' % name)
