import logging
from jenkinsapi.node import Node
from jenkinsapi.exceptions import UnknownNode
from jenkinsapi.jenkinsbase import JenkinsBase

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
        JenkinsBase.__init__(self, baseurl)

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

    def iteritems(self):
        for item in self._data['computer']:
            nodename = item['displayName']
            if nodename.lower() == 'master':
                nodeurl = '%s/(%s)' % (self.baseurl, nodename)
            else:
                nodeurl = '%s/%s' % (self.baseurl, nodename)
            try:
                yield item['displayName'], Node(nodeurl, nodename, self.jenkins)
            except Exception:
                import ipdb; ipdb.set_trace()

    def __getitem__(self, nodename):
        for k, v in self.iteritems():
            if k == nodename:
                return v
        raise UnknownNode(nodename)
