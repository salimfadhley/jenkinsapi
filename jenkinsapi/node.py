"""
Module for jenkinsapi Node class
"""

from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.label import Label
import xml.etree.ElementTree as ET
import logging
import urllib

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
        self._config = None
        self._element_tree = None
        self._labels = None
        JenkinsBase.__init__(self, baseurl)

    def get_jenkins_obj(self):
        return self.jenkins

    def __str__(self):
        return self.name

    def is_online(self):
        self.poll()
        return not self._data['offline']

    def is_temporarily_offline(self):
        self.poll()
        return self._data['temporarilyOffline']

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
            self.poll()
            if not self._data['offline']:
                raise AssertionError("The node state is still online:" +
                                     "offline = %s , temporarilyOffline = %s" %
                                     (self._data['offline'], self._data['temporarilyOffline']))

    def toggle_temporarily_offline(self, message="requested from jenkinsapi"):
        """
        Switches state of connected node (online/offline) and set 'temporarilyOffline' property (True/False)
        Calling the same method again will bring node status back.
        : param message: optional string can be used to explain why you are taking this node offline
        """
        initial_state = self.is_temporarily_offline()
        url = self.baseurl + "/toggleOffline?offlineMessage=" + urllib.quote(message)
        html_result = self.jenkins.requester.get_and_confirm_status(url)
        self.poll()
        log.debug(html_result)
        state = self.is_temporarily_offline()
        if initial_state == state:
            raise AssertionError("The node state has not changed: temporarilyOffline = %s" % state)

    def get_config_xml_url(self):
        return '%s/config.xml' % self.baseurl

    def get_config(self):
        '''Returns the config.xml from the node'''
        response = self.jenkins.requester.get_and_confirm_status(self.get_config_xml_url())
        return response.text

    def load_config(self):
        '''
        Populates the objects _element_tree attribute with a parsed element tree
        from config.xml
        '''
        self._config = self.get_config()
        self._element_tree = ET.fromstring(self._config)

    def _get_labels(self, add_host_label=True):
        if self._element_tree is None:
            self.load_config()
        self._labels = []
        le_text = self._element_tree.find("label").text
        if le_text:
            for label_name in self._element_tree.find('label').text.split(' '):
                self._labels.append(Label(label_name, self.jenkins))
        if add_host_label:
            self._labels.append(Label(self.name, self.jenkins))

    def get_labels(self, add_host_label=True):
        """
        host names are sometimes treated as labels inside a jobs label expression, so we should include
        the hostname as a label by default.
        """
        if self._labels is None:
            self._get_labels(add_host_label)
        return self._labels
