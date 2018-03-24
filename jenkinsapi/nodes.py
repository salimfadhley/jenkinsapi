"""
Module for jenkinsapi nodes
"""
import logging

from six.moves.urllib.parse import urlencode
from jenkinsapi.node import Node
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.custom_exceptions import JenkinsAPIException
from jenkinsapi.custom_exceptions import UnknownNode
from jenkinsapi.custom_exceptions import PostRequired

log = logging.getLogger(__name__)


class Nodes(JenkinsBase):

    """
    Class to hold information on a collection of nodes
    """

    def __init__(self, baseurl, jenkins_obj):
        """
        Handy access to all of the nodes on your Jenkins server
        """
        self.jenkins = jenkins_obj
        JenkinsBase.__init__(self, baseurl.rstrip('/')
                             if '/computer' in baseurl
                             else baseurl.rstrip('/') + '/computer')

    def get_jenkins_obj(self):
        return self.jenkins

    def __str__(self):
        return 'Nodes @ %s' % self.baseurl

    def __contains__(self, node_name):
        return node_name in self.keys()

    def iterkeys(self):
        for item in self._data['computer']:
            yield item['displayName']

    def keys(self):
        return list(self.iterkeys())

    def _make_node(self, nodename):
        """
        Creates an instance of Node for the given nodename.
        This function assumes the returned node exists.
        """
        if nodename.lower() == 'master':
            nodeurl = '%s/(%s)' % (self.baseurl, nodename)
        else:
            nodeurl = '%s/%s' % (self.baseurl, nodename)
        return Node(self.jenkins, nodeurl, nodename, node_dict={})

    def iteritems(self):
        for item in self._data['computer']:
            nodename = item['displayName']
            try:
                yield nodename, self._make_node(nodename)
            except Exception:
                raise JenkinsAPIException('Unable to iterate nodes')

    def __getitem__(self, nodename):
        if nodename in self:
            return self._make_node(nodename)
        raise UnknownNode(nodename)

    def __len__(self):
        return len(self.keys())

    def __delitem__(self, item):
        if item in self and item != 'master':
            url = "%s/doDelete" % self[item].baseurl
            try:
                self.jenkins.requester.get_and_confirm_status(url)
            except PostRequired:
                # Latest Jenkins requires POST here. GET kept for compatibility
                self.jenkins.requester.post_and_confirm_status(url, data={})
            self.poll()
        else:
            if item != 'master':
                raise UnknownNode('Node %s does not exist' % item)
            else:
                log.info('Requests to remove master node ignored')

    def __setitem__(self, name, node_dict):
        if not isinstance(node_dict, dict):
            raise ValueError('"node_dict" parameter must be a Node dict')
        if name not in self:
            self.create_node(name, node_dict)
        self.poll()

    def create_node(self, name, node_dict):
        """
        Create a new slave node

        :param str name: name of slave
        :param dict node_dict: node dict (See Node class)
        :return: node obj
        """
        if name in self:
            return self[name]

        node = Node(jenkins_obj=self.jenkins, baseurl=None, nodename=name,
                    node_dict=node_dict, poll=False)

        url = ('%s/computer/doCreateItem?%s'
               % (self.jenkins.baseurl,
                  urlencode(node.get_node_attributes())))
        data = {'json': urlencode(node.get_node_attributes())}
        self.jenkins.requester.post_and_confirm_status(url, data=data)
        self.poll()
        return self[name]
