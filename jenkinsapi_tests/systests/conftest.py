import os
import logging
import pytest
from jenkinsapi.jenkins import Jenkins
from jenkinsapi_utils.jenkins_launcher import JenkinsLancher

log = logging.getLogger(__name__)
state = {}

# Extra plugins required by the systests
PLUGIN_DEPENDENCIES = [
    "http://updates.jenkins-ci.org/latest/"
    "apache-httpcomponents-client-4-api.hpi",
    "http://updates.jenkins-ci.org/latest/jsch.hpi",
    "http://updates.jenkins-ci.org/latest/workflow-api.hpi",
    "http://updates.jenkins-ci.org/latest/display-url-api.hpi",
    "http://updates.jenkins-ci.org/latest/workflow-step-api.hpi",
    "http://updates.jenkins-ci.org/latest/workflow-scm-step.hpi",
    "http://updates.jenkins-ci.org/latest/icon-shim.hpi",
    "http://updates.jenkins-ci.org/latest/junit.hpi",
    "http://updates.jenkins-ci.org/latest/script-security.hpi",
    "http://updates.jenkins-ci.org/latest/matrix-project.hpi",
    "http://updates.jenkins-ci.org/latest/credentials.hpi",
    "http://updates.jenkins-ci.org/latest/ssh-credentials.hpi",
    "http://updates.jenkins-ci.org/latest/scm-api.hpi",
    "http://updates.jenkins-ci.org/latest/mailer.hpi",
    "http://updates.jenkins-ci.org/latest/git.hpi",
    "http://updates.jenkins-ci.org/latest/git-client.hpi",
    "https://updates.jenkins-ci.org/latest/nested-view.hpi",
    "https://updates.jenkins-ci.org/latest/ssh-slaves.hpi",
    "https://updates.jenkins-ci.org/latest/structs.hpi",
    "http://updates.jenkins-ci.org/latest/plain-credentials.hpi",
    "http://updates.jenkins-ci.org/latest/envinject.hpi",
    "http://updates.jenkins-ci.org/latest/envinject-api.hpi"
]


def _delete_all_jobs(jenkins):
    jenkins.poll()
    for name in jenkins.keys():
        del jenkins[name]


def _delete_all_views(jenkins):
    all_view_names = jenkins.views.keys()[1:]
    for name in all_view_names:
        del jenkins.views[name]


def _delete_all_credentials(jenkins):
    all_cred_names = jenkins.credentials.keys()
    for name in all_cred_names:
        del jenkins.credentials[name]


@pytest.fixture(scope='session')
def launched_jenkins():
    systests_dir, _ = os.path.split(__file__)
    war_path = os.path.join(systests_dir, 'jenkins.war')
    launcher = JenkinsLancher(
        war_path, PLUGIN_DEPENDENCIES,
        jenkins_url=os.getenv('JENKINS_URL', None)
    )
    launcher.start()

    yield launcher

    log.info('All tests finished')
    launcher.stop()


@pytest.fixture(scope='function')
def jenkins(launched_jenkins):
    url = launched_jenkins.jenkins_url

    jenkins_instance = Jenkins(url)

    _delete_all_jobs(jenkins_instance)
    _delete_all_views(jenkins_instance)
    _delete_all_credentials(jenkins_instance)

    return jenkins_instance
