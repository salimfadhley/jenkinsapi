import os
from jenkinsapi_utils.jenkins_launcher import JenkinsLancher
from jenkinsapi_utils.hudson_launcher import HudsonLancher

state = {}

# Extra plugins required by the hudson tests
PLUGIN_DEPENDENCIES = ["http://hudson-ci.org/update-center3/downloads/plugins/birt-charts/3.0.3/birt-charts.hpi",
                       "http://hudson-ci.org/update-center3/downloads/plugins/jna-native-support-plugin/3.0.4/jna-native-support-plugin.hpi",
                       "http://hudson-ci.org/update-center3/downloads/plugins/xpath-provider/1.0.2/xpath-provider.hpi"]


def setUpPackage():
    hudsontests_dir, _ = os.path.split(__file__)

    hudson_war_path = os.path.join(hudsontests_dir, 'hudson.war')
    state['launcher'] = HudsonLancher(hudson_war_path, PLUGIN_DEPENDENCIES)
    print "Starting"
    state['launcher'].start()


def tearDownPackage():
    state['launcher'].stop()
