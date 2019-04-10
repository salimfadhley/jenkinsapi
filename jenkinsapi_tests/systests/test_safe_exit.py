"""
System tests for safeExit jenkins
NB! This test is probelmatic, as it will terminate Jenkins,
and subsequently prevent further tests from running.
It should probably be placed last.

"""
import logging

log = logging.getLogger(__name__)


def test_safe_exit_wait(jenkins):
    jenkins.poll()  # jenkins should be alive
    jenkins.safe_exit(wait_for_exit=True)  # restart and wait for running jobs (default)


def test_safe_exit_dont_wait(jenkins):
    jenkins.poll()  # jenkins should be alive
    jenkins.safe_exit(wait_for_exit=False)  # just terminate jenkins
