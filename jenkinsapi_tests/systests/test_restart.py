"""
System tests for restarting jenkins

NB: this test will be very time consuming because
    after restart it will wait for jenkins to boot
"""
import time
import logging
import pytest
from requests import HTTPError, ConnectionError

log = logging.getLogger(__name__)


def wait_for_reboot(jenkins):
    wait = 5
    count = 0
    max_count = 30
    success = False
    while count < max_count:
        time.sleep(wait)
        try:
            jenkins.poll()
            success = True
        except (HTTPError, ConnectionError):
            msg = ("Jenkins has not restarted yet!  (This is"
                   " try {0} of {1}, waited {2} seconds so far)"
                   "  Sleeping and trying again..")
            msg = msg.format(count, max_count, count*wait)
            log.debug(msg)
        count += 1
    if not success:
        msg = ("Jenkins did not come back from safe restart! "
               "Waited {0} seconds altogether.  This "
               "failure may cause other failures.")
        log.critical(msg.format(count*wait))
        pytest.fail("msg")


def test_safe_restart(jenkins):
    jenkins.poll()  # jenkins should be alive
    jenkins.safe_restart()
    with pytest.raises(HTTPError):
        # this is a 503: jenkins is still restarting
        jenkins.poll()
    # the test is now complete, but other tests cannot run until
    # jenkins has finished restarted.  to avoid cascading failure
    # we have to wait for reboot to finish.
    wait_for_reboot(jenkins)
