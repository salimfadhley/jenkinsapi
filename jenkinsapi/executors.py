"""
This module implements the Executors class, which is intended to be a
container-like interface for all of the executors defined on a single
Jenkins node.
"""
import logging
from jenkinsapi.executor import Executor
from jenkinsapi.jenkinsbase import JenkinsBase

log = logging.getLogger(__name__)


class Executors(JenkinsBase):

    """
    This class provides a container-like API which gives
    access to all executors on a Jenkins node.

    Returns a list of Executor Objects.
    """

    def __init__(self, baseurl, nodename, jenkins):
        self.nodename = nodename
        self.jenkins = jenkins
        JenkinsBase.__init__(self, baseurl)
        self.count = self._data['numExecutors']

    def __str__(self):
        return 'Executors @ %s' % self.baseurl

    def get_jenkins_obj(self):
        return self.jenkins

    def __iter__(self):
        for index in range(self.count):
            executor_url = '%s/executors/%s' % (self.baseurl, index)
            yield Executor(
                executor_url,
                self.nodename,
                self.jenkins,
                index
            )
