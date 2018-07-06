import os
import logging
from jenkinsapi.jenkins import Jenkins


def create_jenkins_object(monkeypatch, jenkins_url, use_baseurl=False):
    def fake_poll(cls, tree=None):   # pylint: disable=unused-argument
        return {}

    monkeypatch.setattr(Jenkins, '_poll', fake_poll)
    new_jenkins = Jenkins(jenkins_url, use_baseurl=use_baseurl)

    return new_jenkins


logging.basicConfig(
    format='%(module)s.%(funcName)s %(levelname)s: %(message)s',
    level=logging.INFO
)

level = logging.WARNING if 'LOG_LEVEL' not in os.environ \
    else os.environ['LOG_LEVEL'].upper().strip()

modules = [
    'requests.packages.urllib3.connectionpool',
    'requests',
    'urllib3',
    'urllib3.connectionpool'
]

for module_name in modules:
    logger = logging.getLogger(module_name)
    logger.setLevel(level)
