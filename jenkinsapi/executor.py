"""
Module for jenkinsapi Executer class
"""

from jenkinsapi.jenkinsbase import JenkinsBase
import logging

log = logging.getLogger(__name__)


class Executor(JenkinsBase):

    """
    Class to hold information on nodes that are attached as slaves to the
    master jenkins instance
    """

    def __init__(self, baseurl, nodename, jenkins_obj, number):
        """
        Init a node object by providing all relevant pointers to it
        :param baseurl: basic url for querying information on a node
        :param nodename: hostname of the node
        :param jenkins_obj: ref to the jenkins obj
        :return: Node obj
        """
        self.nodename = nodename
        self.number = number
        self.jenkins = jenkins_obj
        self.baseurl = baseurl
        JenkinsBase.__init__(self, baseurl)

    def __str__(self):
        return '%s %s' % (self.nodename, self.number)

    def get_jenkins_obj(self):
        return self.jenkins

    def get_progress(self):
        """Returns percentage"""
        return self.poll(tree='progress')['progress']

    def get_number(self):
        """
        Get Executor number.
        """
        return self.poll(tree='number')['number']

    def is_idle(self):
        """
        Returns Boolean: whether Executor is idle or not.
        """
        return self.poll(tree='idle')['idle']

    def likely_stuck(self):
        """
        Returns Boolean: whether Executor is likely stuck or not.
        """
        return self.poll(tree='likelyStuck')['likelyStuck']

    def get_current_executable(self):
        """
        Returns the current Queue.Task this executor is running.
        """
        return self.poll(tree='currentExecutable')['currentExecutable']
