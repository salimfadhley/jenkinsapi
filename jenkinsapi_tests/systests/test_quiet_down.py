"""
System tests for setting jenkins in quietDown mode
"""


def test_quiet_down(jenkins):
    jenkins.poll()  # jenkins should be alive
    jenkins.quiet_down()  # put Jenkins in quietDown mode
    jenkins.poll()  # jenkins should be alive
    jenkins.cancel_quiet_down()  # leave quietDown mode
    jenkins.poll()  # jenkins should be alive
