'''
System tests for `jenkinsapi.jenkins` module.
'''
# To run unittests on python 2.6 please use unittest2 library
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import time
import logging
from jenkinsapi.build import Build
from jenkinsapi.queue import QueueItem
from jenkinsapi_tests.systests.base import BaseSystemTest
from jenkinsapi_tests.test_utils.random_strings import random_string
from jenkinsapi_tests.systests.job_configs import LONG_RUNNING_JOB
from jenkinsapi_tests.systests.job_configs import SHORTISH_JOB, EMPTY_JOB
from jenkinsapi.custom_exceptions import BadParams, NotFound


log = logging.getLogger(__name__)


class TestInvocation(BaseSystemTest):

    def test_invocation_object(self):
        job_name = 'Acreate_%s' % random_string()
        job = self.jenkins.create_job(job_name, SHORTISH_JOB)
        qq = job.invoke()
        self.assertIsInstance(qq, QueueItem)
        # Let Jenkins catchup
        qq.block_until_building()
        self.assertEquals(qq.get_build_number(), 1)

    def test_get_block_until_build_running(self):
        job_name = 'Bcreate_%s' % random_string()
        job = self.jenkins.create_job(job_name, LONG_RUNNING_JOB)
        qq = job.invoke()
        time.sleep(3)
        bn = qq.block_until_building(delay=3).get_number()
        self.assertIsInstance(bn, int)

        b = qq.get_build()
        self.assertIsInstance(b, Build)
        self.assertTrue(b.is_running())
        b.stop()
        # if we call next line right away - Jenkins have no time to stop job
        # so we wait a bit
        time.sleep(1)
        self.assertFalse(b.is_running())
        console = b.get_console()
        self.assertIsInstance(console, str)
        self.assertIn('Started by user', console)

    def test_get_block_until_build_complete(self):
        job_name = 'Ccreate_%s' % random_string()
        job = self.jenkins.create_job(job_name, SHORTISH_JOB)
        qq = job.invoke()
        qq.block_until_complete()
        self.assertFalse(qq.get_build().is_running())

    def test_multiple_invocations_and_get_last_build(self):
        job_name = 'Dcreate_%s' % random_string()

        job = self.jenkins.create_job(job_name, SHORTISH_JOB)

        for _ in range(3):
            ii = job.invoke()
            ii.block_until_complete(delay=2)

        build_number = job.get_last_good_buildnumber()
        self.assertEquals(build_number, 3)

        build = job.get_build(build_number)
        self.assertIsInstance(build, Build)

    def test_multiple_invocations_and_get_build_number(self):
        job_name = 'Ecreate_%s' % random_string()

        job = self.jenkins.create_job(job_name, EMPTY_JOB)

        for invocation in range(3):
            qq = job.invoke()
            qq.block_until_complete(delay=1)
            build_number = qq.get_build_number()
            self.assertEquals(build_number, invocation + 1)

    def test_multiple_invocations_and_delete_build(self):
        job_name = 'Ecreate_%s' % random_string()

        job = self.jenkins.create_job(job_name, EMPTY_JOB)

        for invocation in range(3):
            qq = job.invoke()
            qq.block_until_complete(delay=1)
            build_number = qq.get_build_number()
            self.assertEquals(build_number, invocation + 1)

        # Delete build using Job.delete_build
        job.get_build(1)
        job.delete_build(1)
        with self.assertRaises(NotFound):
            job.get_build(1)

        # Delete build using Job as dictionary of builds
        job[2]
        del job[2]
        with self.assertRaises(NotFound):
            job.get_build(2)

        with self.assertRaises(NotFound):
            job.delete_build(99)

    def test_give_params_on_non_parameterized_job(self):
        job_name = 'Ecreate_%s' % random_string()
        job = self.jenkins.create_job(job_name, EMPTY_JOB)
        with self.assertRaises(BadParams):
            job.invoke(build_params={'foo': 'bar', 'baz': 99})


if __name__ == '__main__':
    #     logging.basicConfig()
    #     logging.getLogger("").setLevel(logging.INFO)
    unittest.main()
