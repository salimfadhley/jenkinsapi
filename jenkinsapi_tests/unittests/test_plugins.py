import mock
import unittest
import time

from jenkinsapi.jenkins import Jenkins
from jenkinsapi.plugins import Plugins
from jenkinsapi.plugin import Plugin


class TestPlugins(unittest.TestCase):
    DATA = {
        'plugins': [
            {
                'deleted': False,
                'hasUpdate': True,
                'downgradable': False,
                'dependencies': [{}, {}, {}, {}],
                'longName': 'Jenkins Subversion Plug-in',
                'active': True,
                'shortName': 'subversion',
                'backupVersion': None,
                'url': 'http://wiki.jenkins-ci.org/display/JENKINS/Subversion+Plugin',
                'enabled': True,
                'pinned': False,
                'version': '1.45',
                'supportsDynamicLoad': 'MAYBE',
                'bundled': True
            },
            {
                'deleted': False,
                'hasUpdate': True,
                'downgradable': False,
                'dependencies': [{}, {}],
                'longName': 'Maven Integration plugin',
                'active': True,
                'shortName': 'maven-plugin',
                'backupVersion': None,
                'url': 'http://wiki.jenkins-ci.org/display/JENKINS/Maven+Project+Plugin',
                'enabled': True,
                'pinned': False,
                'version': '1.521',
                'supportsDynamicLoad': 'MAYBE',
                'bundled': True
            }
        ]
    }

    @mock.patch.object(Jenkins, '_poll')
    def setUp(self, _poll_jenkins):
        _poll_jenkins.return_value = {}

        self.J = Jenkins('http://localhost:8080')

    @mock.patch.object(Plugins, '_poll')
    def test_get_plugins(self, _poll_plugins):
        _poll_plugins.return_value = self.DATA

        # Can we produce a repr string for this object
        self.assertIsInstance(self.J.get_plugins(), Plugins)

    @mock.patch.object(Plugins, '_poll')
    def test_no_plugins_str(self, _poll_plugins):
        _poll_plugins.return_value = {}

        plugins = self.J.get_plugins()
        self.assertEquals(str(plugins), "[]")

    @mock.patch.object(Plugins, '_poll')
    def test_plugins_str(self, _poll_plugins):
        _poll_plugins.return_value = self.DATA

        plugins = self.J.get_plugins()
        self.assertEquals(str(plugins), "['maven-plugin', 'subversion']")

    @mock.patch.object(Plugins, '_poll')
    def test_plugins_len(self, _poll_plugins):
        _poll_plugins.return_value = self.DATA

        plugins = self.J.get_plugins()
        self.assertEquals(len(plugins), 2)

    @mock.patch.object(Plugins, '_poll')
    def test_plugins_contains(self, _poll_plugins):
        _poll_plugins.return_value = self.DATA

        plugins = self.J.get_plugins()
        self.assertIn('subversion', plugins)
        self.assertIn('maven-plugin', plugins)

    @mock.patch.object(Plugins, '_poll')
    def test_plugins_values(self, _poll_plugins):
        _poll_plugins.return_value = self.DATA

        p = Plugin(
            {
                'deleted': False,
                'hasUpdate': True,
                'downgradable': False,
                'dependencies': [{}, {}, {}, {}],
                'longName': 'Jenkins Subversion Plug-in',
                'active': True,
                'shortName': 'subversion',
                'backupVersion': None,
                'url': 'http://wiki.jenkins-ci.org/display/JENKINS/Subversion+Plugin',
                'enabled': True,
                'pinned': False,
                'version': '1.45',
                'supportsDynamicLoad': 'MAYBE',
                'bundled': True
            }
        )

        plugins = self.J.get_plugins().values()
        self.assertIn(p, plugins)

    @mock.patch.object(Plugins, '_poll')
    def test_plugins_keys(self, _poll_plugins):
        _poll_plugins.return_value = self.DATA

        plugins = self.J.get_plugins().keys()
        self.assertIn('subversion', plugins)
        self.assertIn('maven-plugin', plugins)

    @mock.patch.object(Plugins, '_poll')
    def test_plugins_empty(self, _poll_plugins):
        _poll_plugins.return_value = {}

        plugins = self.J.get_plugins().keys()
        self.assertEquals([], plugins)

    @mock.patch.object(Plugins, '_poll')
    def test_plugin_get_by_name(self, _poll_plugins):
        _poll_plugins.return_value = self.DATA

        p = Plugin(
            {
                'deleted': False,
                'hasUpdate': True,
                'downgradable': False,
                'dependencies': [{}, {}, {}, {}],
                'longName': 'Jenkins Subversion Plug-in',
                'active': True,
                'shortName': 'subversion',
                'backupVersion': None,
                'url': 'http://wiki.jenkins-ci.org/display/JENKINS/Subversion+Plugin',
                'enabled': True,
                'pinned': False,
                'version': '1.45',
                'supportsDynamicLoad': 'MAYBE',
                'bundled': True
            }
        )

        plugin = self.J.get_plugins()['subversion']
        self.assertEquals(p, plugin)

    @mock.patch.object(Plugins, '_poll')
    def test_poll_cache(self, _poll):
        # only gets called once in interval
        plugins = Plugins('http://', self.J, poll_cache_timeout=1)
        for i in range(2):
            plugins.poll()
        self.assertEquals(_poll.call_count, 1)
        plugins.poll(True)  # test force poll
        self.assertEquals(_poll.call_count, 2)

        # ensure it gets called again after cache timeout
        _poll.reset_mock()
        time.sleep(1.1)
        plugins.poll()
        self.assertTrue(_poll.called)

        # ensure it is disabled by default
        _poll.reset_mock()
        plugins = self.J.get_plugins()
        for i in range(2):
            plugins.poll()
        self.assertEquals(_poll.call_count, 3)  # get plugins triggers a poll
        self.assertIsNone(plugins.poll_cache_expires)


if __name__ == '__main__':
    unittest.main()
