'''
System tests for `jenkinsapi.jenkins` module.
'''
import re
import time
# To run unittests on python 2.6 please use unittest2 library
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from jenkinsapi_tests.systests.base import BaseSystemTest
from jenkinsapi_tests.systests.job_configs import MATRIX_JOB
from jenkinsapi_tests.test_utils.random_strings import random_string


class TestMatrixJob(BaseSystemTest):

    def test_invoke_matrix_job(self):
        job_name = 'create_%s' % random_string()
        job = self.jenkins.create_job(job_name, MATRIX_JOB)
        queueItem = job.invoke()
        queueItem.block_until_complete()

        build = job.get_last_build()

        while build.is_running():
            time.sleep(1)

        set_of_groups = set()
        for run in build.get_matrix_runs():
            self.assertEquals(run.get_number(), build.get_number())
            self.assertEquals(run.get_upstream_build(), build)
            match_result = re.search(u'\xbb (.*) #\\d+$', run.name)
            self.assertIsNotNone(match_result)
            set_of_groups.add(match_result.group(1))
            build.get_master_job_name()

        # This is a bad test, it simply verifies that this function does
        # not crash on a build from a matrix job.
        self.assertFalse(build.get_master_job_name())

        self.assertEqual(set_of_groups, set(['one', 'two', 'three']))

if __name__ == '__main__':
    unittest.main()
