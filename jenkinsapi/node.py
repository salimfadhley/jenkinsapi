"""
Module for jenkinsapi Node class
"""

from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.custom_exceptions import PostRequired
import logging

try:
    from urllib import quote as urlquote
except ImportError:
    # Python3
    from urllib.parse import quote as urlquote

log = logging.getLogger(__name__)


class Node(JenkinsBase):
    """
    Class to hold information on nodes that are attached as slaves to the master jenkins instance
    """

    def __init__(self, baseurl, nodename, jenkins_obj):
        """
        Init a node object by providing all relevant pointers to it
        :param baseurl: basic url for querying information on a node
        :param nodename: hostname of the node
        :param jenkins_obj: ref to the jenkins obj
        :return: Node obj
        """
        self.name = nodename
        self.jenkins = jenkins_obj
        JenkinsBase.__init__(self, baseurl)

    def get_jenkins_obj(self):
        return self.jenkins

    def __str__(self):
        return self.name

    def is_online(self):
        return not self.poll(tree='offline')['offline']

    def is_temporarily_offline(self):
        return self.poll(tree='temporarilyOffline')['temporarilyOffline']

    def is_jnlpagent(self):
        return self._data['jnlpAgent']

    def is_idle(self):
        return self._data['idle']

    def set_online(self):
        """
        Set node online.
        Before change state verify client state: if node set 'offline' but 'temporarilyOffline'
        is not set - client has connection problems and AssertionError raised.
        If after run node state has not been changed raise AssertionError.
        """
        self.poll()
        # Before change state check if client is connected
        if self._data['offline'] and not self._data['temporarilyOffline']:
            raise AssertionError("Node is offline and not marked as temporarilyOffline" +
                                 ", check client connection: " +
                                 "offline = %s , temporarilyOffline = %s" %
                                 (self._data['offline'], self._data['temporarilyOffline']))
        elif self._data['offline'] and self._data['temporarilyOffline']:
            self.toggle_temporarily_offline()
            if self._data['offline']:
                raise AssertionError("The node state is still offline, check client connection:" +
                                     " offline = %s , temporarilyOffline = %s" %
                                     (self._data['offline'], self._data['temporarilyOffline']))

    def set_offline(self, message="requested from jenkinsapi"):
        """
        Set node offline.
        If after run node state has not been changed raise AssertionError.
        : param message: optional string explain why you are taking this node offline
        """
        if not self._data['offline']:
            self.toggle_temporarily_offline(message)
            data = self.poll(tree='offline,temporarilyOffline')
            if not data['offline']:
                raise AssertionError("The node state is still online:" +
                                     "offline = %s , temporarilyOffline = %s" %
                                     (data['offline'], data['temporarilyOffline']))

    def toggle_temporarily_offline(self, message="requested from jenkinsapi"):
        """
        Switches state of connected node (online/offline) and set 'temporarilyOffline' property (True/False)
        Calling the same method again will bring node status back.
        : param message: optional string can be used to explain why you are taking this node offline
        """
        initial_state = self.is_temporarily_offline()
        url = self.baseurl + "/toggleOffline?offlineMessage=" + urlquote(message)
        try:
            html_result = self.jenkins.requester.get_and_confirm_status(url)
        except PostRequired:
            html_result = self.jenkins.requester.post_and_confirm_status(url, data={})

        self.poll()
        log.debug(html_result)
        state = self.is_temporarily_offline()
        if initial_state == state:
            raise AssertionError("The node state has not changed: temporarilyOffline = %s" % state)
