"""
System tests for restarting jenkins

NB: this test will be very time consuming because
    after restart it will wait for jenkins to boot
"""
import time
import logging

# To run unittests on python 2.6 please use unittest2 library
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from jenkinsapi_tests.systests.base import BaseSystemTest

log = logging.getLogger(__name__)


class TestRestart(BaseSystemTest):

    def test_safe_restart(self):
        self.jenkins.poll()  # jenkins should be alive
        self.jenkins.safe_restart(wait_for_reboot=True)
        self.jenkins.poll()  # This will only succeed on successful reboot

if __name__ == '__main__':
    logging.basicConfig()
    unittest.main()
