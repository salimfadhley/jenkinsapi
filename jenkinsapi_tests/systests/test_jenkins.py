'''
System tests for `jenkinsapi.jenkins` module.
'''
# To run unittests on python 2.6 please use unittest2 library
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from jenkinsapi.job import Job
from jenkinsapi.jobs import Jobs
from jenkinsapi.queue import QueueItem
from jenkinsapi_tests.systests.base import BaseSystemTest
from jenkinsapi_tests.systests.job_configs import EMPTY_JOB
from jenkinsapi_tests.test_utils.random_strings import random_string
from jenkinsapi.custom_exceptions import UnknownJob


class JobTests(BaseSystemTest):

    def test_create_job(self):
        job_name = 'create_%s' % random_string()
        self.jenkins.create_job(job_name, EMPTY_JOB)
        self.assertJobIsPresent(job_name)

    def test_create_job_with_plus(self):
        job_name = 'create+%s' % random_string()
        self.jenkins.create_job(job_name, EMPTY_JOB)
        self.assertJobIsPresent(job_name)
        job = self.jenkins[job_name]
        self.assertTrue(job_name in job.url)

    def test_create_dup_job(self):
        job_name = 'create_%s' % random_string()
        old_job = self.jenkins.create_job(job_name, EMPTY_JOB)
        self.assertJobIsPresent(job_name)
        new_job = self.jenkins.create_job(job_name, EMPTY_JOB)
        self.assertEquals(new_job, old_job)

    def test_get_jobs_info(self):
        job_name = 'create_%s' % random_string()
        job = self.jenkins.create_job(job_name, EMPTY_JOB)

        jobs_info = list(self.jenkins.get_jobs_info())
        self.assertEqual(len(jobs_info), 1)
        for url, name in jobs_info:
            self.assertEqual(url, job.url)
            self.assertEqual(name, job.name)

    def test_create_job_through_jobs_dict(self):
        job_name = 'create_%s' % random_string()
        self.jenkins.jobs[job_name] = EMPTY_JOB
        self.assertJobIsPresent(job_name)

    def test_enable_disable_job(self):
        job_name = 'create_%s' % random_string()
        self.jenkins.create_job(job_name, EMPTY_JOB)
        self.assertJobIsPresent(job_name)

        j = self.jenkins[job_name]
        j.invoke(block=True)  # run this at least once

        j.disable()
        self.assertEquals(
            j.is_enabled(),
            False,
            'A disabled job is reporting incorrectly')
        j.enable()
        self.assertEquals(
            j.is_enabled(),
            True,
            'An enabled job is reporting incorrectly')

    def test_get_job_and_update_config(self):
        job_name = 'config_%s' % random_string()
        self.jenkins.create_job(job_name, EMPTY_JOB)
        self.assertJobIsPresent(job_name)
        config = self.jenkins[job_name].get_config()
        self.assertEquals(config.strip(), EMPTY_JOB.strip())
        self.jenkins[job_name].update_config(EMPTY_JOB)

    def test_invoke_job(self):
        job_name = 'create_%s' % random_string()
        job = self.jenkins.create_job(job_name, EMPTY_JOB)
        job.invoke()

    def test_invocation_object(self):
        job_name = 'create_%s' % random_string()
        job = self.jenkins.create_job(job_name, EMPTY_JOB)
        ii = job.invoke()
        self.assertIsInstance(ii, QueueItem)

    def test_get_jobs_list(self):
        job1_name = 'first_%s' % random_string()
        job2_name = 'second_%s' % random_string()

        self._create_job(job1_name)
        self._create_job(job2_name)
        job_list = self.jenkins.get_jobs_list()
        self.assertGreaterEqual(len(self.jenkins.jobs), 2)
        self.assertEqual([job1_name, job2_name], job_list)

    def test_get_job(self):
        job1_name = 'first_%s' % random_string()

        self._create_job(job1_name)
        job = self.jenkins[job1_name]
        self.assertIsInstance(job, Job)
        self.assertEqual(job.name, job1_name)

    def test_get_jobs(self):
        job1_name = 'first_%s' % random_string()
        job2_name = 'second_%s' % random_string()

        self._create_job(job1_name)
        self._create_job(job2_name)
        jobs = self.jenkins.jobs
        self.assertIsInstance(jobs, Jobs)
        self.assertGreaterEqual(len(jobs), 2)
        for job_name, job in jobs.iteritems():
            self.assertIsInstance(job_name, str)
            self.assertIsInstance(job, Job)

    def test_get_job_that_does_not_exist(self):
        with self.assertRaises(UnknownJob):
            self.jenkins['doesnot_exist']

    def test_has_job(self):
        job1_name = 'first_%s' % random_string()
        self._create_job(job1_name)
        self.assertTrue(self.jenkins.has_job(job1_name))
        self.assertTrue(job1_name in self.jenkins)

    def test_has_no_job(self):
        self.assertFalse(self.jenkins.has_job('doesnt_exist'))
        self.assertTrue('doesnt_exist' not in self.jenkins)

    def test_delete_job(self):
        job1_name = 'delete_me_%s' % random_string()

        self._create_job(job1_name)
        self.jenkins.delete_job(job1_name)
        self.assertJobIsAbsent(job1_name)

    def test_rename_job(self):
        job1_name = 'A__%s' % random_string()
        job2_name = 'B__%s' % random_string()

        self._create_job(job1_name)
        self.jenkins.rename_job(job1_name, job2_name)
        self.assertJobIsAbsent(job1_name)
        self.assertJobIsPresent(job2_name)

    def test_copy_job(self):

        template_job_name = 'TPL%s' % random_string()
        copied_job_name = 'CPY%s' % random_string()

        self._create_job(template_job_name)
        j = self.jenkins.copy_job(template_job_name, copied_job_name)
        self.assertJobIsPresent(template_job_name)
        self.assertJobIsPresent(copied_job_name)
        self.assertIsInstance(j, Job)
        self.assertEquals(j.name, copied_job_name)

    def test_get_master_data(self):
        master_data = self.jenkins.get_master_data()
        self.assertEquals(master_data['totalExecutors'], 2)


if __name__ == '__main__':
    unittest.main()
