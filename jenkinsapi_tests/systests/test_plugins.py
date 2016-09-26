'''
System tests for `jenkinsapi.plugins` module.
'''
import logging
# To run unittests on python 2.6 please use unittest2 library
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import jenkinsapi_tests.systests
from jenkinsapi_tests.systests.base import BaseSystemTest
from jenkinsapi_tests.systests.base import DEFAULT_JENKINS_PORT
from jenkinsapi_tests.test_utils.random_strings import random_string
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.plugin import Plugin

log = logging.getLogger(__name__)


class TestPlugins(BaseSystemTest):

    @classmethod
    def setUpClass(cls):
        try:
            port = jenkinsapi_tests.systests.state['launcher'].http_port
        except KeyError:
            log.warning(
                "Jenkins was not launched from the test-framework, "
                "assuming port %i" %
                DEFAULT_JENKINS_PORT)
            port = DEFAULT_JENKINS_PORT
        jenkins = Jenkins('http://localhost:%d' % port)
        plugins = jenkins.plugins
        plugins.check_updates_server()

    def test_delete_inexistant_plugin(self):
        with self.assertRaises(KeyError):
            plugins = self.jenkins.plugins

            del plugins[random_string()]

    def test_install_uninstall_plugin(self):
        plugins = self.jenkins.plugins
        plugin_name = 'async-http-client'

        plugin_dict = {
            'shortName': plugin_name,
            'version': 'latest',
        }
        plugins[plugin_name] = Plugin(plugin_dict)

        self.assertTrue(plugin_name in plugins)
        plugin = plugins[plugin_name]
        self.assertIsInstance(plugin, Plugin)
        self.assertEquals(plugin.shortName, plugin_name)

        del plugins[plugin_name]
        self.assertTrue(plugins[plugin_name].deleted)

    def test_install_multiple_plugins(self):
        plugin_one_name = 'jenkins-cloudformation-plugin'
        plugin_one_version = 'latest'
        plugin_one = "@".join((plugin_one_name, plugin_one_version))
        plugin_two = Plugin({'shortName': 'anything-goes-formatter', 'version': 'latest'})
        self.assertIsInstance(plugin_two, Plugin)
        plugin_list = [plugin_one, plugin_two]
        self.jenkins.install_plugins(plugin_list)
        self.assertIn(plugin_one_name, self.jenkins.plugins)
        self.assertIn(plugin_two.shortName, self.jenkins.plugins)

    def test_downgrade_plugin(self):
        plugin_name = 'amazon-ecs'
        plugin_version = '1.5'
        plugin = Plugin({'shortName': plugin_name, 'version': plugin_version})
        self.assertIsInstance(plugin, Plugin)
        self.jenkins.plugins[plugin_name] = plugin
        installed_plugin = self.jenkins.plugins[plugin_name]
        self.assertEquals(installed_plugin.version, '1.5')
        older_plugin = Plugin({'shortName': plugin_name, 'version': '1.4'})
        # Need to restart when changing version
        self.jenkins.install_plugins([older_plugin], restart=True, wait_for_reboot=True)
        installed_older_plugin = self.jenkins.plugins[plugin_name]
        self.assertEquals(installed_older_plugin.version, '1.4')

    def test_get_missing_plugin(self):
        plugins = self.jenkins.get_plugins()
        with self.assertRaises(KeyError):
            plugins["lsdajdaslkjdlkasj"]  # this plugin surely does not exist!

    def test_get_single_plugin(self):
        plugins = self.jenkins.get_plugins()
        plugin_name, plugin = next(plugins.iteritems())
        self.assertIsInstance(plugin_name, str)
        self.assertIsInstance(plugin, Plugin)

    def test_get_single_plugin_depth_2(self):
        plugins = self.jenkins.get_plugins(depth=2)
        _, plugin = next(plugins.iteritems())
