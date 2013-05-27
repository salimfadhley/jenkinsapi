'''
System tests for `jenkinsapi.jenkins` module.
'''
from jenkinsapi_tests.systests.base import BaseSystemTest, EMPTY_JOB_CONFIG


class JobTests(BaseSystemTest):

    def test_create_job(self):
        self.jenkins.create_job('whatever', EMPTY_JOB_CONFIG)
        self.assertJobIsPresent('whatever')

    def test_get_jobs_list(self):
        self._create_job('job1')
        self._create_job('job2')
        job_list = self.jenkins.get_jobs_list()
        self.assertEqual(['job1', 'job2'], job_list)

    def test_delete_job(self):
        self._create_job('job_to_delete')
        self.jenkins.delete_job('job_to_delete')
        self.assertJobIsAbsent('job_to_delete')

    def test_rename_job(self):
        self._create_job('job_to_rename')
        self.jenkins.rename_job('job_to_rename', 'renamed_job')
        self.assertJobIsAbsent('job_to_rename')
        self.assertJobIsPresent('renamed_job')

    def test_copy_job(self):
        self._create_job('template_job')
        self.jenkins.copy_job('template_job', 'copied_job')
        self.assertJobIsPresent('template_job')
        self.assertJobIsPresent('copied_job')


class NodeTests(BaseSystemTest):

    def test_get_node_dict(self):
        self.assertEqual(self.jenkins.get_node_dict(), {
            'master': 'http://localhost:8080/computer/master/api/python/'})
