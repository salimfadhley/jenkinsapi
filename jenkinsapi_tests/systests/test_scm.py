'''
System tests for `jenkinsapi.jenkins` module.
'''
import unittest
from jenkinsapi.invocation import Invocation
from jenkinsapi_tests.systests import state
from jenkinsapi_tests.systests.base import BaseSystemTest
from jenkinsapi_tests.test_utils.random_strings import random_string
from jenkinsapi_tests.systests.job_configs import SCM_GIT_JOB

# Maybe have a base class for all SCM test activites?
class TestSCMGIT(BaseSystemTest):
    # Maybe it makes sense to move plugin dependencies outside the code.
    # Have a config to dependencies mapping from the launcher can use to install plugins.
    PLUGIN_DEPENDENCIES = ["http://updates.jenkins-ci.org/latest/git.hpi",
                           "http://updates.jenkins-ci.org/latest/git-client.hpi"]
    
    def test_get_revision(self):
        job_name = 'create_%s' % random_string()
        state['launcher'].install_plugin(self.PLUGIN_DEPENDENCIES)
        job = self.jenkins.create_job(job_name, SCM_GIT_JOB)
        ii = job.invoke()
        ii.block(until='completed')
        self.assertFalse(ii.is_running())
        b = ii.get_build()
        self.assertIsInstance(b.get_revision(), basestring)

if __name__ == '__main__':
    unittest.main()

