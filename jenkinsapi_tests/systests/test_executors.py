'''
System tests for `jenkinsapi.jenkins` module.
'''

from jenkinsapi_tests.systests.base import BaseSystemTest
from jenkinsapi_tests.systests.job_configs import LONG_RUNNING_JOB
from jenkinsapi_tests.test_utils.random_strings import random_string
import logging
import time
import unittest


log = logging.getLogger(__name__)


class TestNodes(BaseSystemTest):

    def test_get_executors(self):
        node_name = random_string()
        self.jenkins.create_node(node_name)
        executors = self.jenkins.get_executors(node_name)
        self.assertEqual(executors.count, 2)
        for count, execs in enumerate(executors):
            self.assertEqual(count, execs.get_number())
            self.assertEqual(execs.is_idle(), True)

    def test_running_executor(self):
        node_name = random_string()
        self.jenkins.create_node(node_name)
        job_name = 'create_%s' % random_string()
        job = self.jenkins.create_job(job_name, LONG_RUNNING_JOB)
        ii = job.invoke(invoke_pre_check_delay=2)
        ii.block(until='not_queued')
        
        if job.is_running() is False:
            time.sleep(1)
        executors = self.jenkins.get_executors(node_name)
        all_idle = True
        for execs in executors:
            if execs.is_idle() is False:
                all_idle = False
                self.assertNotEqual(execs.get_progress(), -1)
                self.assertEqual(execs.get_current_executable(), ii.get_build_number())
                self.assertEqual(execs.likely_stuck(), False)
        self.assertEqual(all_idle, True, "Executor should have been triggered.")

    def test_idle_executors(self):
        node_name = random_string()
        self.jenkins.create_node(node_name)
        executors = self.jenkins.get_executors(node_name)

        for execs in executors:
            self.assertEqual(execs.get_progress(), -1)
            self.assertEqual(execs.get_current_executable(), None)
            self.assertEqual(execs.likely_stuck(), False)
            self.assertEqual(execs.is_idle(), True)


if __name__ == '__main__':
    logging.basicConfig()
    unittest.main()
