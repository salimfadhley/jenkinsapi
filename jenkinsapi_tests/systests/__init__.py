import os
from jenkinsapi_utils.jenkins_launcher import JenkinsLancher

state = {}

# Extra plugins required by the systests
PLUGIN_DEPENDENCIES = [
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
    "https://updates.jenkins-ci.org/latest/structs.hpi"
]


def setUpPackage():
    systests_dir, _ = os.path.split(__file__)
    war_path = os.path.join(systests_dir, 'jenkins.war')
    state['launcher'] = JenkinsLancher(
        war_path, PLUGIN_DEPENDENCIES,
        jenkins_url=os.getenv('JENKINS_URL', None))
    state['launcher'].start()


def tearDownPackage():
    state['launcher'].stop()
