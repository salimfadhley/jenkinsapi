'''
System tests for `jenkinsapi.jenkins` module.
'''
import time
import logging
# To run unittests on python 2.6 please use unittest2 library
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from jenkinsapi.queue import Queue
from jenkinsapi.queue import QueueItem
from jenkinsapi.job import Job
from jenkinsapi_tests.systests.base import BaseSystemTest
from jenkinsapi_tests.test_utils.random_strings import random_string
from jenkinsapi_tests.systests.job_configs import LONG_RUNNING_JOB

log = logging.getLogger(__name__)


class TestQueue(BaseSystemTest):
    """
    All kinds of testing on Jenkins Queues
    """
    # TODO: Test timeout behavior

    def test_get_queue(self):
        qq = self.jenkins.get_queue()
        self.assertIsInstance(qq, Queue)

    def test_invoke_many_jobs(self):
        job_names = [random_string() for _ in range(5)]
        jobs = []

        while len(self.jenkins.get_queue()) != 0:
            log.info('Sleeping to get queue empty...')
            time.sleep(1)

        for job_name in job_names:
            j = self.jenkins.create_job(job_name, LONG_RUNNING_JOB)
            jobs.append(j)
            j.invoke()

            self.assertTrue(j.is_queued_or_running())

        queue = self.jenkins.get_queue()

        reprString = repr(queue)
        self.assertIn(queue.baseurl, reprString)
        self.assertTrue(len(queue) == 5, queue.keys())
        self.assertIsInstance(queue[queue.keys()[0]].get_job(), Job)
        items = queue.get_queue_items_for_job(job_names[2])
        self.assertIsInstance(items, list)
        self.assertEquals(len(items), 1)
        self.assertIsInstance(items[0], QueueItem)
        self.assertEquals(items[0].get_parameters(), [])

        for _, item in queue.iteritems():
            queue.delete_item(item)

        queue.poll()

        self.assertEquals(len(queue), 0)

    def test_start_and_stop_long_running_job(self):
        job_name = random_string()
        j = self.jenkins.create_job(job_name, LONG_RUNNING_JOB)
        j.invoke()
        time.sleep(1)
        self.assertTrue(j.is_queued_or_running())

        while j.is_queued():
            time.sleep(0.5)

        if j.is_running():
            time.sleep(1)

        j.get_first_build().stop()
        time.sleep(1)
        self.assertFalse(j.is_queued_or_running())

    def test_queueitem_for_why_field(self):
        # Make some jobs just in case there aren't any.
        job_names = [random_string() for _ in range(2)]
        jobs = []
        for job_name in job_names:
            j = self.jenkins.create_job(job_name, LONG_RUNNING_JOB)
            jobs.append(j)
            j.invoke()

        queue = self.jenkins.get_queue()
        for _, item in queue.iteritems():
            self.assertIsInstance(item.why, str)

        # Clean up after ourselves
        for _, item in queue.iteritems():
            queue.delete_item(item)

if __name__ == '__main__':
    logging.basicConfig()
    unittest.main()
