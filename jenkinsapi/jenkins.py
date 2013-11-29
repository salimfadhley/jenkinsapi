"""
Module for jenkinsapi Jenkins object
"""


import json
import urllib
import logging
import urlparse

from jenkinsapi import config
from jenkinsapi.executors import Executors
from jenkinsapi.job import Job
from jenkinsapi.jobs import Jobs
from jenkinsapi.node import Node
from jenkinsapi.view import View
from jenkinsapi.nodes import Nodes
from jenkinsapi.plugins import Plugins
from jenkinsapi.views import Views
from jenkinsapi.queue import Queue
from jenkinsapi.fingerprint import Fingerprint
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.utils.requester import Requester
from jenkinsapi.custom_exceptions import UnknownJob

log = logging.getLogger(__name__)


class Jenkins(JenkinsBase):
    """
    Represents a jenkins environment.
    """
    def __init__(self, baseurl, username=None, password=None, requester=None):
        """
        :param baseurl: baseurl for jenkins instance including port, str
        :param username: username for jenkins auth, str
        :param password: password for jenkins auth, str
        :return: a Jenkins obj
        """
        self.username = username
        self.password = password
        self.requester = requester or Requester(username, password, baseurl=baseurl)
        JenkinsBase.__init__(self, baseurl)

    def _clone(self):
        return Jenkins(self.baseurl, username=self.username,
                       password=self.password, requester=self.requester)

    def base_server_url(self):
        if config.JENKINS_API in self.baseurl:
            return self.baseurl[:-(len(config.JENKINS_API))]
        else:
            return self.baseurl

    def validate_fingerprint(self, id_):
        obj_fingerprint = Fingerprint(self.baseurl, id_, jenkins_obj=self)
        obj_fingerprint.validate()
        log.info(msg="Jenkins says %s is valid" % id_)

    # def reload(self):
    #     '''Try and reload the configuration from disk'''
    #     self.requester.get_url("%(baseurl)s/reload" % self.__dict__)

    def get_artifact_data(self, id_):
        obj_fingerprint = Fingerprint(self.baseurl, id_, jenkins_obj=self)
        obj_fingerprint.validate()
        return obj_fingerprint.get_info()

    def validate_fingerprint_for_build(self, digest, filename, job, build):
        obj_fingerprint = Fingerprint(self.baseurl, digest, jenkins_obj=self)
        return obj_fingerprint.validate_for_build(filename, job, build)

    def get_jenkins_obj(self):
        return self

    def get_jenkins_obj_from_url(self, url):
        return Jenkins(url, self.username, self.password, self.requester)

    def get_create_url(self):
        # This only ever needs to work on the base object
        return '%s/createItem' % self.baseurl

    def get_nodes_url(self):
        # This only ever needs to work on the base object
        return '%s/computer' % self.baseurl

    @property
    def jobs(self):
        return Jobs(self)

    def get_jobs(self):
        """
        Fetch all the build-names on this Jenkins server.
        """
        for info in self._data["jobs"]:
            yield info["name"], \
                Job(info["url"], info["name"], jenkins_obj=self)

    def get_jobs_info(self):
        """
        Get the jobs information
        :return url, name
        """
        for info in self._data["jobs"]:
            yield info["url"], info["name"]

    def get_job(self, jobname):
        """
        Get a job by name
        :param jobname: name of the job, str
        :return: Job obj
        """
        return self.jobs[jobname]

    def has_job(self, jobname):
        """
        Does a job by the name specified exist
        :param jobname: string
        :return: boolean
        """
        return jobname in self.jobs

    def create_job(self, jobname, config_):
        """
        Create a job
        :param jobname: name of new job, str
        :param config: configuration of new job, xml
        :return: new Job obj
        """
        return self.jobs.create(jobname, config_)

    def copy_job(self, jobname, newjobname):
        return self.jobs.copy(jobname, newjobname)

    def build_job(self, jobname, params=None):
        """
        Invoke a build by job name
        :param jobname: name of exist job, str
        :param params: the job params, dict
        :return: none
        """
        self[jobname].invoke(build_params=params or {})

    def delete_job(self, jobname):
        """
        Delete a job by name
        :param jobname: name of a exist job, str
        :return: new jenkins_obj
        """
        del self.jobs[jobname]

    def rename_job(self, jobname, newjobname):
        """
        Rename a job
        :param jobname: name of a exist job, str
        :param newjobname: name of new job, str
        :return: new Job obj
        """
        return self.jobs.rename(jobname, newjobname)

    def iterkeys(self):
        for info in self._data["jobs"]:
            yield info["name"]

    def iteritems(self):
        """
        :param return: An iterator of pairs.
            Each pair will be (job name, Job object)
        """
        return self.get_jobs()

    def items(self):
        """
        :param return: A list of pairs. Each pair will be (job name, Job object)
        """
        return list(self.get_jobs())

    def keys(self):
        return [a for a in self.iterkeys()]

    # This is a function alias we retain for historical compatibility
    get_jobs_list = keys

    def __str__(self):
        return "Jenkins server at %s" % self.baseurl

    @property
    def views(self):
        return Views(self)

    def get_view_by_url(self, str_view_url):
        #for nested view
        str_view_name = str_view_url.split('/view/')[-1].replace('/', '')
        return View(str_view_url, str_view_name, jenkins_obj=self)

    def delete_view_by_url(self, str_url):
        url = "%s/doDelete" % str_url
        self.requester.post_and_confirm_status(url, data='')
        self.poll()
        return self

    def __getitem__(self, jobname):
        """
        Get a job by name
        :param jobname: name of job, str
        :return: Job obj
        """
        for info in self._data["jobs"]:
            if info["name"] == jobname:
                return Job(info["url"], info["name"], jenkins_obj=self)
        raise UnknownJob(jobname)

    def __len__(self):
        return len(self._data["jobs"])

    def __contains__(self, jobname):
        """
        Does a job by the name specified exist
        :param jobname: string
        :return: boolean
        """
        return jobname in self.jobs

    def get_node(self, nodename):
        """Get a node object for a specific node"""
        return self.get_nodes()[nodename]

    def get_node_url(self, nodename=""):
        """Return the url for nodes"""
        url = urlparse.urljoin(self.base_server_url(), 'computer/%s' % urllib.quote(nodename))
        return url

    def get_queue_url(self):
        url = "%s/%s" % (self.base_server_url(), 'queue')
        return url

    def get_queue(self):
        queue_url = self.get_queue_url()
        return Queue(queue_url, self)

    def get_nodes(self):
        url = self.get_nodes_url()
        return Nodes(url, self)

    def has_node(self, nodename):
        """
        Does a node by the name specified exist
        :param nodename: string, hostname
        :return: boolean
        """
        self.poll()
        return nodename in self.get_nodes()

    def delete_node(self, nodename):
        """
        Remove a node from the managed slave list
        Please note that you cannot remove the master node

        :param nodename: string holding a hostname
        :return: None
        """
        assert self.has_node(nodename), "This node: %s is not registered as a slave" % nodename
        assert nodename != "master", "you cannot delete the master node"
        url = "%s/doDelete" % self.get_node_url(nodename)
        self.requester.get_and_confirm_status(url)

    def create_node(self, name, num_executors=2, node_description=None,
                    remote_fs='/var/lib/jenkins', labels=None, exclusive=False):
        """
        Create a new slave node by name.

        :param name: fqdn of slave, str
        :param num_executors: number of executors, int
        :param node_description: a freetext field describing the node
        :param remote_fs: jenkins path, str
        :param labels: labels to associate with slave, str
        :param exclusive: tied to specific job, boolean
        :return: node obj
        """
        NODE_TYPE = 'hudson.slaves.DumbSlave$DescriptorImpl'
        MODE = 'NORMAL'
        if self.has_node(name):
            return Node(nodename=name, baseurl=self.get_node_url(nodename=name), jenkins_obj=self)
        if exclusive:
            MODE = 'EXCLUSIVE'
        params = {
            'name': name,
            'type': NODE_TYPE,
            'json': json.dumps({
                'name': name,
                'nodeDescription': node_description,
                'numExecutors': num_executors,
                'remoteFS': remote_fs,
                'labelString': labels,
                'mode': MODE,
                'type': NODE_TYPE,
                'retentionStrategy': {'stapler-class': 'hudson.slaves.RetentionStrategy$Always'},
                'nodeProperties': {'stapler-class-bag': 'true'},
                'launcher': {'stapler-class': 'hudson.slaves.JNLPLauncher'}
            })
        }
        url = self.get_node_url() + "doCreateItem?%s" % urllib.urlencode(params)
        self.requester.get_and_confirm_status(url)

        return Node(nodename=name, baseurl=self.get_node_url(nodename=name), jenkins_obj=self)

    def get_plugins_url(self):
        # This only ever needs to work on the base object
        return '%s/pluginManager/api/python?depth=1' % self.baseurl

    def get_plugins(self):
        url = self.get_plugins_url()
        return Plugins(url, self)

    def has_plugin(self, plugin_name):
        return plugin_name in self.get_plugins()

    def get_executors(self, nodename):
        url = '%s/computer/%s' % (self.baseurl, nodename)
        return Executors(url, nodename, self)
