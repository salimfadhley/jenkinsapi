"""
jenkinsapi plugins
"""
from __future__ import print_function

import logging
import time
import zipfile
try:
    from StringIO import StringIO
    from urllib import urlencode
except ImportError:
    # Python3
    from io import StringIO
    from urllib.parse import urlencode
import requests
from jenkinsapi.plugin import Plugin
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.custom_exceptions import UnknownPlugin
from jenkinsapi.custom_exceptions import JenkinsAPIException


log = logging.getLogger(__name__)


class Plugins(JenkinsBase):

    """
    Plugins class for jenkinsapi
    """

    def __init__(self, url, jenkins_obj):
        self.jenkins_obj = jenkins_obj
        JenkinsBase.__init__(self, url)
        # print('DEBUG: Plugins._data=', self._data)

    def get_jenkins_obj(self):
        return self.jenkins_obj

    def check_updates_server(self):
        url = (
            '%s/pluginManager/checkUpdatesServer'
            % self.jenkins_obj.baseurl
        )
        self.jenkins_obj.requester.post_and_confirm_status(url, params={}, data={})

    def _poll(self, tree=None):
        return self.get_data(self.baseurl, tree=tree)

    def keys(self):
        return self.get_plugins_dict().keys()

    __iter__ = keys

    def iteritems(self):
        return self._get_plugins()

    def values(self):
        return [a[1] for a in self.iteritems()]

    def _get_plugins(self):
        if 'plugins' in self._data:
            for p_dict in self._data["plugins"]:
                yield p_dict["shortName"], Plugin(p_dict)

    def get_plugins_dict(self):
        return dict(self._get_plugins())

    def __len__(self):
        return len(self.get_plugins_dict().keys())

    def __getitem__(self, plugin_name):
        try:
            return self.get_plugins_dict()[plugin_name]
        except KeyError:
            raise UnknownPlugin(plugin_name)

    def __setitem__(self, shortName, plugin):
        """
        Installs plugin in Jenkins.

        If plugin already exists - this method is going to uninstall the existing
        plugin and install the specified version.

        :param shortName: Plugin ID
        :param plugin a Plugin object to be installed.
        """
        if plugin.is_latest(self.jenkins_obj.update_center_dict):
            self._install_plugin_from_updatecenter(plugin)
        else:
            self._install_specific_version(plugin)
        self._wait_until_plugin_installed(shortName)

    def _install_plugin_from_updatecenter(self, plugin):
        """
        Latest versions of plugins can be installed from the update center (and don't need a restart.)
        """
        xml_str = plugin.get_attributes()
        url = (
            '%s/pluginManager/installNecessaryPlugins' % self.jenkins_obj.baseurl
        )
        self.jenkins_obj.requester.post_xml_and_confirm_status(url, data=xml_str)

    def _install_specific_version(self, plugin):
        """
        Plugins that are not the latest version have to be uploaded.
        """
        download_link = plugin.get_download_link(update_center_dict=self.jenkins_obj.update_center_dict)
        downloaded_plugin = StringIO()
        downloaded_plugin.write(requests.get(download_link).content)
        self._install_plugin_dependencies(downloaded_plugin)
        url = ('%s/pluginManager/uploadPlugin' % self.jenkins_obj.baseurl)
        requester = self.jenkins_obj.requester
        downloaded_plugin.seek(0)
        requester.post_and_confirm_status(url, files={'file': ('plugin.hpi', downloaded_plugin)}, data={}, params={})

    def _install_plugin_dependencies(self, downloaded_plugin):
        with zipfile.ZipFile(downloaded_plugin) as archive:
            for line in archive.open('META-INF/MANIFEST.MF'):
                if line.startswith('Plugin-Dependencies: '):
                    dependencies = line.strip().split('Plugin-Dependencies: ')[1].split(',')
                    for dep in dependencies:
                        name, _ = dep.split(':')
                        # install latest dependency, avoids multiple versions of the same dep
                        self.jenkins_obj.plugins[name] = Plugin({'shortName': name, 'version': 'latest'})

    def __delitem__(self, shortName):
        if shortName not in self:
            raise KeyError(
                'Plugin with ID "%s" not found, cannot uninstall' % shortName)
        if self[shortName].deleted:
            raise JenkinsAPIException('Plugin "%s" already marked for uninstall. '
                                      'Restart jenkins for uninstall to complete.')
        params = {
            'Submit': 'OK',
            'json': {}
        }
        url = ('%s/pluginManager/plugin/%s/doUninstall'
               % (self.jenkins_obj.baseurl, shortName))
        self.jenkins_obj.requester.post_and_confirm_status(
            url, params={}, data=urlencode(params)
        )

        self.poll()
        self.plugins = self._data['plugins']
        if not self[shortName].deleted:
            raise JenkinsAPIException('Problem uninstalling plugin.')

    def _wait_until_plugin_installed(self, shortName, maxwait=60, interval=1):
        for time_left in range(maxwait, 0, -interval):
            self.poll()
            self.plugins = self._data['plugins']
            if shortName in self:
                return
            time.sleep(interval)
        raise JenkinsAPIException('Problem installing plugin.')

    def __contains__(self, plugin_name):
        """
        True if plugin_name is the name of a defined plugin
        """
        return plugin_name in self.keys()

    def __str__(self):
        plugins = [plugin["shortName"]
                   for plugin in self._data.get("plugins", [])]
        return str(sorted(plugins))
