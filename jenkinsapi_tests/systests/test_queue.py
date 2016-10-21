"""
All kinds of testing on Jenkins Queues
"""
import time
import logging
from jenkinsapi.queue import Queue
from jenkinsapi.queue import QueueItem
from jenkinsapi.job import Job
from jenkinsapi_tests.test_utils.random_strings import random_string
from jenkinsapi_tests.systests.job_configs import LONG_RUNNING_JOB

log = logging.getLogger(__name__)


def test_get_queue(jenkins):
    qq = jenkins.get_queue()
    assert isinstance(qq, Queue) is True


def test_invoke_many_jobs(jenkins):
    job_names = [random_string() for _ in range(5)]
    jobs = []

    while len(jenkins.get_queue()) != 0:
        log.info('Sleeping to get queue empty...')
        time.sleep(1)

    for job_name in job_names:
        j = jenkins.create_job(job_name, LONG_RUNNING_JOB)
        jobs.append(j)
        j.invoke()

        assert j.is_queued_or_running() is True

    queue = jenkins.get_queue()

    reprString = repr(queue)
    assert queue.baseurl in reprString
    assert len(queue) == 5, queue.keys()
    assert isinstance(queue[queue.keys()[0]].get_job(), Job) is True
    items = queue.get_queue_items_for_job(job_names[2])
    assert isinstance(items, list) is True
    assert len(items) == 1
    assert isinstance(items[0], QueueItem) is True
    assert items[0].get_parameters() == []

    for _, item in queue.iteritems():
        queue.delete_item(item)

    queue.poll()

    assert len(queue) == 0


def test_start_and_stop_long_running_job(jenkins):
    job_name = random_string()
    j = jenkins.create_job(job_name, LONG_RUNNING_JOB)
    j.invoke()
    time.sleep(1)
    assert j.is_queued_or_running() is True

    while j.is_queued():
        time.sleep(0.5)

    if j.is_running():
        time.sleep(1)

    j.get_first_build().stop()
    time.sleep(1)
    assert j.is_queued_or_running() is False


def test_queueitem_for_why_field(jenkins):
    # Make some jobs just in case there aren't any.
    job_names = [random_string() for _ in range(2)]
    jobs = []
    for job_name in job_names:
        j = jenkins.create_job(job_name, LONG_RUNNING_JOB)
        jobs.append(j)
        j.invoke()

    queue = jenkins.get_queue()
    for _, item in queue.iteritems():
        assert isinstance(item.why, str) is True

    # Clean up after ourselves
    for _, item in queue.iteritems():
        queue.delete_item(item)
