'''
System tests for `jenkinsapi.jenkins` module.
'''
import os
import re
import time
import gzip
import shutil
import tempfile
import unittest

from jenkinsapi_tests.systests.base import BaseSystemTest
from jenkinsapi_tests.systests.job_configs import MATRIX_JOB
from jenkinsapi_tests.test_utils.random_strings import random_string


class TestPingerJob(BaseSystemTest):

    def test_invoke_job(self):
        job_name = 'create_%s' % random_string()
        job = self.jenkins.create_job(job_name, MATRIX_JOB)
        job.invoke(block=True)

        b = job.get_last_build()

        while b.is_running():
            time.sleep(1)

        s = set()
        for r in b.get_matrix_runs():
            self.assertEquals(r.get_number(), b.get_number())
            self.assertEquals(r.get_upstream_build(), b)
            m = re.search(u'\xbb (.*) #\\d+$', r.name)
            self.assertIsNotNone(m)
            s.add(m.group(1))
        self.assertEqual(s, {'one', 'two', 'three'})

if __name__ == '__main__':
    unittest.main()
