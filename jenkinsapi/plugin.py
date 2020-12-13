"""
Module for jenkinsapi Plugin
"""

from typing import Any, Dict


class Plugin(object):

    """
    Plugin class
    """

    def __init__(self, plugin_dict):
        # TODO: forcing the __dict__ so that the values become properties of
        # the class instance is convenient, but dangerous since it makes
        # type hinting more difficult, amongst other concerns.
        if isinstance(plugin_dict, dict):
            self.__dict__ = plugin_dict
        else:
            self.__dict__ = self.to_plugin(plugin_dict)

    def to_plugin(self, plugin_string):
        # type: (str) -> Dict[str, str]
        plugin_string = str(plugin_string)
        if '@' not in plugin_string or len(plugin_string.split('@')) != 2:
            usage_err = ('plugin specification must be a string like '
                         '"plugin-name@version", not "{0}"')
            usage_err = usage_err.format(plugin_string)
            raise ValueError(usage_err)

        shortName, version = plugin_string.split('@')
        return {'shortName': shortName, 'version': version}

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        # TODO: this works because the __dict__ from jenkins has a shortName
        # entry. We might want to reconsider this approach.
        return self.shortName   # type: ignore

    def __repr__(self):
        return "<%s.%s %s>" % (
            self.__class__.__module__,
            self.__class__.__name__,
            str(self)
        )

    def get_attributes(self):
        """
        Used by Plugins object to install plugins in Jenkins
        """
        return (
            "<jenkins> <install plugin=\"%s@%s\" /> </jenkins>"
            % (self.shortName, self.version)    # type: ignore
        )

    def is_latest(self, update_center_dict):
        # type: (Dict[str, Any]) -> bool
        """
        Used by Plugins object to determine if plugin can be
        installed through the update center (when plugin version is
        latest version), or must be installed by uploading
        the plugin hpi file.
        """
        if self.version == 'latest':    # type: ignore
            return True
        center_plugin = update_center_dict['plugins'][self.shortName]   # type: ignore
        return center_plugin['version'] == self.version     # type: ignore

    def get_download_link(self, update_center_dict):
        # type: (Dict[str, Any]) -> str
        latest_version = update_center_dict[
            'plugins'][self.shortName]['version']   # type: ignore
        latest_url = update_center_dict['plugins'][self.shortName]['url']   # type: ignore
        return latest_url.replace(
            "/".join(
                (self.shortName, latest_version)),  # type: ignore
            "/".join((self.shortName, self.version)))   # type: ignore
