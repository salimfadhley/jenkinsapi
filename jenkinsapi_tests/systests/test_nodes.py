'''
System tests for `jenkinsapi.jenkins` module.
'''
import logging
import unittest
from jenkinsapi_tests.systests.base import BaseSystemTest
from jenkinsapi_tests.test_utils.random_strings import random_string

log = logging.getLogger(__name__)


class TestNodes(BaseSystemTest):

    def test_invoke_job_parameterized(self):
        node_name = random_string()
        self.jenkins.create_node(node_name)
        self.assertTrue(self.jenkins.has_node(node_name))

        N = self.jenkins.get_node(node_name)
        self.assertEquals(N.baseurl, self.jenkins.get_node_url(node_name))

        self.jenkins.delete_node(node_name)
        self.assertFalse(self.jenkins.has_node(node_name))

    def test_online_offline(self):
        """
        Can we flip the online / offline state of the master node.
        """
        # Master node name should be case insensitive
        # mn0 = self.jenkins.get_node('MaStEr')
        mn = self.jenkins.get_node('master')
        # self.assertEquals(mn, mn0)

        mn.set_online()  # It should already be online, hence no-op
        self.assertTrue(mn.is_online())

        mn.set_offline()  # We switch that suckah off
        mn.set_offline()  # This should be a no-op
        self.assertFalse(mn.is_online())

        mn.set_online()  # Switch it back on
        self.assertTrue(mn.is_online())


if __name__ == '__main__':
    logging.basicConfig()
    unittest.main()
