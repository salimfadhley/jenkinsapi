"""
jenkinsapi plugins
"""

import logging

from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.plugin import Plugin


log = logging.getLogger(__name__)


class Plugins(JenkinsBase):
    """
    Plugins class for jenkinsapi
    """
    def __init__(self, url, jenkins_obj):
        self.jenkins_obj = jenkins_obj
        JenkinsBase.__init__(self, url)
        # print 'DEBUG: Plugins._data=', self._data

    def get_jenkins_obj(self):
        return self.jenkins_obj

    def _poll(self):
        return self.get_data(self.baseurl)

    def keys(self):
        return self.get_plugins_dict().keys()

    def iteritems(self):
        return self._get_plugins()

    def values(self):
        return [a[1] for a in self.iteritems()]

    def _get_plugins(self):
        if not 'plugins' in self._data:
            pass
        else:
            for p_dict in self._data["plugins"]:
                yield p_dict["shortName"], Plugin(p_dict)

    def get_plugins_dict(self):
        return dict(self._get_plugins())

    def __len__(self):
        return len(self.get_plugins_dict().keys())

    def __getitem__(self, plugin_name):
        return self.get_plugins_dict().get(plugin_name, None)

    def __contains__(self, plugin_name):
        """
        True if plugin_name is the name of a defined plugin
        """
        return plugin_name in self.keys()

    def __str__(self):
        plugins = [plugin["shortName"] for plugin in self._data.get("plugins", [])]
        return str(sorted(plugins))
