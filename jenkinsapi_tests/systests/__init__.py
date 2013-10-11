import os
from jenkinsapi_utils.jenkins_launcher import JenkinsLancher

state = {}

# Extra plugins required by the systests
PLUGIN_DEPENDENCIES = ["http://updates.jenkins-ci.org/latest/git.hpi",
                       "http://updates.jenkins-ci.org/latest/git-client.hpi",
                       "https://updates.jenkins-ci.org/latest/nested-view.hpi"]


def setUpPackage():
    systests_dir, _ = os.path.split(__file__)
    war_path = os.path.join(systests_dir, 'jenkins.war')
    state['launcher'] = JenkinsLancher(war_path, PLUGIN_DEPENDENCIES)
    state['launcher'].start()


def tearDownPackage():
    state['launcher'].stop()
