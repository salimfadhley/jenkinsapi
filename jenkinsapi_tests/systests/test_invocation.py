'''
System tests for `jenkinsapi.jenkins` module.
'''
import unittest
from jenkinsapi.build import Build
from jenkinsapi.invocation import Invocation
from jenkinsapi_tests.systests.base import BaseSystemTest
from jenkinsapi_tests.test_utils.random_strings import random_string
from jenkinsapi_tests.systests.job_configs import LONG_RUNNING_JOB
from jenkinsapi_tests.systests.job_configs import SHORTISH_JOB, EMPTY_JOB


class TestInvocation(BaseSystemTest):

    def test_invocation_object(self):
        job_name = 'create_%s' % random_string()
        job = self.jenkins.create_job(job_name, LONG_RUNNING_JOB)
        ii = job.invoke(invoke_pre_check_delay=7)
        self.assertIsInstance(ii, Invocation)
        self.assertTrue(ii.is_queued_or_running())
        self.assertEquals(ii.get_build_number(), 1)

    def test_get_block_until_build_running(self):
        job_name = 'create_%s' % random_string()
        job = self.jenkins.create_job(job_name, LONG_RUNNING_JOB)
        ii = job.invoke(invoke_pre_check_delay=7)
        bn = ii.get_build_number()
        self.assertIsInstance(bn, int)
        ii.block(until='not_queued')
        self.assertTrue(ii.is_running())
        b = ii.get_build()
        self.assertIsInstance(b, Build)
        ii.stop()
        self.assertFalse(ii.is_running())
        self.assertIsInstance(ii.get_build().get_console(), str)
        self.assertIn('Started by user', ii.get_build().get_console())

    def test_get_block_until_build_complete(self):
        job_name = 'create_%s' % random_string()
        job = self.jenkins.create_job(job_name, SHORTISH_JOB)
        ii = job.invoke()
        ii.block(until='completed')
        self.assertFalse(ii.is_running())

    def test_multiple_invocations_and_get_last_build(self):
        job_name = 'create_%s' % random_string()

        job = self.jenkins.create_job(job_name, SHORTISH_JOB)

        for _ in range(3):
            ii = job.invoke()
            ii.block(until='completed')

        build_number = job.get_last_good_buildnumber()
        self.assertEquals(build_number, 3)

        build = job.get_build(build_number)
        self.assertIsInstance(build, Build)

    def test_multiple_invocations_and_get_build_number(self):
        job_name = 'create_%s' % random_string()

        job = self.jenkins.create_job(job_name, EMPTY_JOB)

        for invocation in range(3):
            ii = job.invoke()
            ii.block(until='completed')
            build_number = ii.get_build_number()
            self.assertEquals(build_number, invocation + 1)


if __name__ == '__main__':
    unittest.main()
