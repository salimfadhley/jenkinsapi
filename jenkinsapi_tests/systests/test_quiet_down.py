
"""
System tests for setting jenkins in quietDown mode
"""
import pytest
import logging


log = logging.getLogger(__name__)


@pytest.mark.run_these_please
def test_quiet_down_and_cancel_quiet_down(jenkins):
    jenkins.poll()  # jenkins should be alive
    jenkins.quiet_down()  # put Jenkins in quietDown mode

    jenkins_api = jenkins.get_api_python_data()
    is_quieting_down = jenkins_api['quietingDown']
    assert is_quieting_down is True

    jenkins.poll()  # jenkins should be alive

    jenkins.cancel_quiet_down()  # leave quietDown mode
    jenkins_api = jenkins.get_api_python_data()
    is_quieting_down = jenkins_api['quietingDown']
    assert is_quieting_down is False

    jenkins.poll()  # jenkins should be alive
