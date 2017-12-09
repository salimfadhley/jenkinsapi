"""
Module for jenkinsapi Node class
"""
import json
import logging

import xml.etree.ElementTree as ET

from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.custom_exceptions import PostRequired
from jenkinsapi.custom_exceptions import JenkinsAPIException
from six.moves.urllib.parse import quote as urlquote

log = logging.getLogger(__name__)


class Node(JenkinsBase):

    """
    Class to hold information on nodes that are attached as slaves
    to the master jenkins instance
    """

    def __init__(self, jenkins_obj, baseurl, nodename, node_dict, poll=True):
        """
        Init a node object by providing all relevant pointers to it
        :param jenkins_obj: ref to the jenkins obj
        :param baseurl: basic url for querying information on a node
            If url is not set - object will construct it itself. This is
            useful when node is being created and not exists in Jenkins yet
        :param nodename: hostname of the node
        :param dict node_dict: Dict with node parameters as described below
        :param bool poll: set to False if node does not exist or automatic
            refresh from Jenkins is not required. Default is True.
            If baseurl parameter is set to None - poll parameter will be
            set to False

        JNLP Node:
            {
                'num_executors': int,
                'node_description': str,
                'remote_fs': str,
                'labels': str,
                'exclusive': bool
            }

        SSH Node:
        {
            'num_executors': int,
            'node_description': str,
            'remote_fs': str,
            'labels': str,
            'exclusive': bool,
            'host': str,
            'port': int
            'credential_description': str,
            'jvm_options': str,
            'java_path': str,
            'prefix_start_slave_cmd': str,
            'suffix_start_slave_cmd': str
            'max_num_retries': int,
            'retry_wait_time': int,
            'retention': str ('Always' or 'OnDemand')
            'ondemand_delay': int (only for OnDemand retention)
            'ondemand_idle_delay': int (only for OnDemand retention)
            'env': [
                {
                    'key':'TEST',
                    'value':'VALUE'
                },
                {
                    'key':'TEST2',
                    'value':'value2'
                }
            ],
            'tool_location': [
                {
                    "key": "hudson.tasks.Maven$MavenInstallation$DescriptorImpl@Maven 3.0.5",
                    "home": "/home/apache-maven-3.0.5/"
                },
                {
                    "key": "hudson.plugins.git.GitTool$DescriptorImpl@Default",
                    "home": "/home/git-3.0.5/"
                },
            ]
        }

        :return: None
        :return: Node obj
        """
        self.name = nodename
        self.jenkins = jenkins_obj
        if not baseurl:
            poll = False
            baseurl = '%s/computer/%s' % (self.jenkins.baseurl, self.name)
        JenkinsBase.__init__(self, baseurl, poll=poll)
        self.node_attributes = node_dict
        self._element_tree = None
        self._config = None

    def get_node_attributes(self):
        """
        Gets node attributes as dict

        Used by Nodes object when node is created

        :return: Node attributes dict formatted for Jenkins API request
            to create node
        """
        na = self.node_attributes
        if not na.get('credential_description', False):
            # If credentials description is not present - we will create
            # JNLP node
            launcher = {'stapler-class': 'hudson.slaves.JNLPLauncher'}
        else:
            try:
                credential = self.jenkins.credentials[
                    na['credential_description']
                ]
            except KeyError:
                raise JenkinsAPIException('Credential with description "%s"'
                                          ' not found'
                                          % na['credential_description'])

            retries = na['max_num_retries'] if 'max_num_retries' in na else ''
            re_wait = na['retry_wait_time'] if 'retry_wait_time' in na else ''
            launcher = {
                'stapler-class': 'hudson.plugins.sshslaves.SSHLauncher',
                '$class': 'hudson.plugins.sshslaves.SSHLauncher',
                'host': na['host'],
                'port': na['port'],
                'credentialsId': credential.credential_id,
                'jvmOptions': na['jvm_options'],
                'javaPath': na['java_path'],
                'prefixStartSlaveCmd': na['prefix_start_slave_cmd'],
                'suffixStartSlaveCmd': na['suffix_start_slave_cmd'],
                'maxNumRetries': retries,
                'retryWaitTime': re_wait
            }

        retention = {
            'stapler-class': 'hudson.slaves.RetentionStrategy$Always',
            '$class': 'hudson.slaves.RetentionStrategy$Always'
        }
        if 'retention' in na and na['retention'].lower() == 'ondemand':
            retention = {
                'stapler-class': 'hudson.slaves.RetentionStrategy$Demand',
                '$class': 'hudson.slaves.RetentionStrategy$Demand',
                'inDemandDelay': na['ondemand_delay'],
                'idleDelay': na['ondemand_idle_delay']
            }

        node_props = {
            'stapler-class-bag': 'true'
        }
        if 'env' in na:
            node_props.update({
                'hudson-slaves-EnvironmentVariablesNodeProperty': {
                    'env': na['env']
                }
            })
        if 'tool_location' in na:
            node_props.update({
                "hudson-tools-ToolLocationNodeProperty": {
                    "locations": na['tool_location']
                }
            })

        params = {
            'name': self.name,
            'type': 'hudson.slaves.DumbSlave$DescriptorImpl',
            'json': json.dumps({
                'name': self.name,
                'nodeDescription': na['node_description'],
                'numExecutors': na['num_executors'],
                'remoteFS': na['remote_fs'],
                'labelString': na['labels'],
                'mode': 'EXCLUSIVE' if na['exclusive'] else 'NORMAL',
                'retentionStrategy': retention,
                'type': 'hudson.slaves.DumbSlave',
                'nodeProperties': node_props,
                'launcher': launcher
            })
        }

        return params

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
        Before change state verify client state: if node set 'offline'
        but 'temporarilyOffline' is not set - client has connection problems
        and AssertionError raised.
        If after run node state has not been changed raise AssertionError.
        """
        self.poll()
        # Before change state check if client is connected
        if self._data['offline'] and not self._data['temporarilyOffline']:
            raise AssertionError("Node is offline and not marked as "
                                 "temporarilyOffline, check client "
                                 "connection: offline = %s, "
                                 "temporarilyOffline = %s" %
                                 (self._data['offline'],
                                  self._data['temporarilyOffline']))
        elif self._data['offline'] and self._data['temporarilyOffline']:
            self.toggle_temporarily_offline()
            if self._data['offline']:
                raise AssertionError("The node state is still offline, "
                                     "check client connection:"
                                     " offline = %s, "
                                     "temporarilyOffline = %s" %
                                     (self._data['offline'],
                                      self._data['temporarilyOffline']))

    def set_offline(self, message="requested from jenkinsapi"):
        """
        Set node offline.
        If after run node state has not been changed raise AssertionError.
        : param message: optional string explain why you are taking this
            node offline
        """
        if not self._data['offline']:
            self.toggle_temporarily_offline(message)
            data = self.poll(tree='offline,temporarilyOffline')
            if not data['offline']:
                raise AssertionError("The node state is still online:" +
                                     "offline = %s , temporarilyOffline = %s" %
                                     (data['offline'],
                                      data['temporarilyOffline']))

    def toggle_temporarily_offline(self, message="requested from jenkinsapi"):
        """
        Switches state of connected node (online/offline) and
        set 'temporarilyOffline' property (True/False)
        Calling the same method again will bring node status back.
        :param message: optional string can be used to explain why you
            are taking this node offline
        """
        initial_state = self.is_temporarily_offline()
        url = self.baseurl + \
            "/toggleOffline?offlineMessage=" + urlquote(message)
        try:
            html_result = self.jenkins.requester.get_and_confirm_status(url)
        except PostRequired:
            html_result = self.jenkins.requester.post_and_confirm_status(
                url,
                data={})

        self.poll()
        log.debug(html_result)
        state = self.is_temporarily_offline()
        if initial_state == state:
            raise AssertionError(
                "The node state has not changed: temporarilyOffline = %s" %
                state)

    @property
    def _et(self):
        return self._get_config_element_tree()

    def _get_config_element_tree(self):
        """
        Returns an xml element tree for the node's config.xml. The
        resulting tree is cached for quick lookup.
        """
        if self._config is None:
            self.load_config()

        if self._element_tree is None:
            self._element_tree = ET.fromstring(self._config)
        return self._element_tree

    def get_config(self):
        """
        Returns the config.xml from the node.
        """
        response = self.jenkins.requester.get_and_confirm_status(
            "%(baseurl)s/config.xml" % self.__dict__)
        return response.text

    def load_config(self):
        """
        Loads the config.xml for the node allowing it to be re-queried
        without generating new requests.
        """
        if self.name == 'master':
            raise JenkinsAPIException('master node does not have config.xml')

        self._config = self.get_config()
        self._get_config_element_tree()

    def upload_config(self, config_xml):
        """
        Uploads config_xml to the config.xml for the node.
        """
        if self.name == 'master':
            raise JenkinsAPIException('master node does not have config.xml')

        self.jenkins.requester.post_and_confirm_status(
            "%(baseurl)s/config.xml" % self.__dict__,
            data=config_xml)

    def get_labels(self):
        """
        Returns the labels for a slave as a string with each label
        separated by the ' ' character.
        """
        return self.get_config_element('label')

    def get_num_executors(self):
        try:
            return self.get_config_element('numExecutors')
        except JenkinsAPIException:
            return self._data['numExecutors']

    def set_num_executors(self, value):
        """
        Sets number of executors for node

        Warning! Setting number of executors on master node will erase all
        other settings
        """
        set_value = value if isinstance(value, str) else str(value)

        if self.name == 'master':
            # master node doesn't have config.xml, so we're going to submit
            # form here
            data = 'json=%s' % urlquote(
                json.dumps({
                    "numExecutors": set_value,
                    "nodeProperties": {
                        "stapler-class-bag": "true"
                    }
                })
            )

            url = self.baseurl + '/configSubmit'
            self.jenkins.requester.post_and_confirm_status(url, data=data)
        else:
            self.set_config_element('numExecutors', set_value)

        self.poll()

    def get_config_element(self, el_name):
        """
        Returns simple config element.

        Better not to be used to return "nodeProperties" or "launcher"
        """
        return self._et.find(el_name).text

    def set_config_element(self, el_name, value):
        """
        Sets simple config element
        """
        self._et.find(el_name).text = value
        xml_str = ET.tostring(self._et)
        self.upload_config(xml_str)
