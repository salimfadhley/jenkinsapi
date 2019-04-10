"""
System tests for safeExit jenkins
NB! This test is probelmatic, as it will terminate Jenkins,
and subsequently might prevent further tests from running.
Attempted marked as last

"""
import logging
import pytest

log = logging.getLogger(__name__)


@pytest.mark.last
def test_safe_exit_wait(jenkins):
    jenkins.poll()  # jenkins should be alive
    jenkins.safe_exit(wait_for_exit=True)  # restart and wait for running jobs (default)
