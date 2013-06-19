import os
from jenkinsapi_utils.jenkins_launcher import JenkinsLancher

state={}

def setUpPackage():
    systests_dir, _ = os.path.split(__file__)
    war_path = os.path.join(systests_dir, 'jenkins.war' )
    state['launcher'] = JenkinsLancher(war_path)

    state['launcher'].start()

def tearDownPackage():
    state['launcher'].stop()
