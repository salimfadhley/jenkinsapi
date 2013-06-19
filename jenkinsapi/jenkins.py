import json
import urllib
import logging

from jenkinsapi import config
from jenkinsapi.job import Job
from jenkinsapi.node import Node
from jenkinsapi.view import View
from jenkinsapi.nodes import Nodes
from jenkinsapi.views import Views
from jenkinsapi.queue import Queue
from jenkinsapi.fingerprint import Fingerprint
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.utils.requester import Requester
from jenkinsapi.exceptions import UnknownJob, JenkinsAPIException



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
        self.requester = requester or Requester(username, password)
        JenkinsBase.__init__(self, baseurl)

    def _clone(self):
        return Jenkins(self.baseurl, username=self.username, password=self.password, requester=self.requester)

    def base_server_url(self):
        if config.JENKINS_API in self.baseurl:
            return self.baseurl[:-(len(config.JENKINS_API))]
        else:
            return self.baseurl

    def validate_fingerprint(self, id):
        obj_fingerprint = Fingerprint(self.baseurl, id, jenkins_obj=self)
        obj_fingerprint.validate()
        log.info("Jenkins says %s is valid" % id)

    # def reload(self):
    #     '''Try and reload the configuration from disk'''
    #     self.requester.get_url("%(baseurl)s/reload" % self.__dict__)

    def get_artifact_data(self, id):
        obj_fingerprint = Fingerprint(self.baseurl, id, jenkins_obj=self)
        obj_fingerprint.validate()
        return obj_fingerprint.get_info()

    def validate_fingerprint_for_build(self, digest, filename, job, build):
        obj_fingerprint = Fingerprint(self.baseurl, digest, jenkins_obj=self)
        return obj_fingerprint.validate_for_build(filename, job, build)

    def get_jenkins_obj(self):
        return self

    def get_create_url(self):
        # This only ever needs to work on the base object
        return '%s/createItem' % self.baseurl

    def get_nodes_url(self):
        # This only ever needs to work on the base object
        return '%s/computer' % self.baseurl

    def get_jobs(self):
        """
        Fetch all the build-names on this Jenkins server.
        """
        for info in self._data["jobs"]:
            yield info["name"], Job(info["url"], info["name"], jenkins_obj=self)

    def get_jobs_info(self):
        """
        Get the jobs information
        :return url, name
        """
        for info in self._data["jobs"]:
            yield info["url"], info["name"]

    def get_jobs_list(self):
        """
        return jobs dict,'name:url'
        """
        jobs = []
        for info in self._data["jobs"]:
            jobs.append(info["name"])
        return jobs

    def get_job(self, jobname):
        """
        Get a job by name
        :param jobname: name of the job, str
        :return: Job obj
        """
        return self[jobname]

    def has_job(self, jobname):
        """
        Does a job by the name specified exist
        :param jobname: string
        :return: boolean
        """
        return jobname in self

    def create_job(self, jobname, config):
        """
        Create a job
        :param jobname: name of new job, str
        :param config: configuration of new job, xml
        :return: new Job obj
        """
        if self.has_job(jobname):
            return self[jobname]

        params = {'name': jobname}
        self.requester.post_xml_and_confirm_status(self.get_create_url(), data=config, params=params)
        self.poll()
        if not self.has_job(jobname):
            raise JenkinsAPIException('Cannot create job %s' % jobname)
        return self[jobname]

    def copy_job(self, jobname, newjobname):
        """
        Copy a job
        :param jobname: name of a exist job, str
        :param newjobname: name of new job, str
        :return: new Job obj
        """
        params = { 'name': newjobname,
                   'mode': 'copy',
                   'from': jobname}

        self.requester.post_and_confirm_status(
            self.get_create_url(),
            params=params,
            data='')
        self.poll()
        return self[jobname]

    def build_job(self, jobname, params={}):
        """
        Invoke a build by job name
        :param jobname: name of exist job, str
        :param params: the job params, dict
        :return: none
        """
        self[jobname].invoke(params=params)
        return

    def delete_job(self, jobname):
        """
        Delete a job by name
        :param jobname: name of a exist job, str
        :return: new jenkins_obj
        """
        delete_job_url = self[jobname].get_delete_url()
        self.requester.post_and_confirm_status(
            delete_job_url,
            data='some random bytes...'
        )
        self.poll()
        return self

    def rename_job(self, jobname, newjobname):
        """
        Rename a job
        :param jobname: name of a exist job, str
        :param newjobname: name of new job, str
        :return: new Job obj
        """
        params = {'newName': newjobname}
        rename_job_url = self[jobname].get_rename_url()
        self.requester.post_and_confirm_status(
            rename_job_url, params=params, data='')
        self.poll()
        return self[newjobname]

    def iterkeys(self):
        for info in self._data["jobs"]:
            yield info["name"]

    def iteritems(self):
        """
        :param return: An iterator of pairs. Each pair will be (job name, Job object)
        """
        return self.get_jobs()

    def items(self):
        """
        :param return: A list of pairs. Each pair will be (job name, Job object)
        """
        return list(self.get_jobs())

    def keys(self):
        return [ a for a in self.iterkeys() ]

    def __str__(self):
        return "Jenkins server at %s" % self.baseurl

    def views(self):
        return Views(self)

    def get_view_by_url(self, str_view_url):
        #for nested view
        str_view_name = str_view_url.split('/view/')[-1].replace('/', '')
        return View(str_view_url , str_view_name, jenkins_obj=self)

    def __getitem__(self, jobname):
        """
        Get a job by name
        :param jobname: name of job, str
        :return: Job obj
        """
        for name, job in self.get_jobs():
            if name == jobname:
                return job
        raise UnknownJob(jobname)

    def __contains__(self, jobname):
        """
        Does a job by the name specified exist
        :param jobname: string
        :return: boolean
        """
        return jobname in self.get_jobs_list()

    def get_node(self, nodename):
        """Get a node object for a specific node"""
        return self.get_nodes()[nodename]

    def get_node_url(self, nodename=""):
        """Return the url for nodes"""
        url = "%(baseurl)s/computer/%(nodename)s" % {'baseurl': self.baseurl, 'nodename': urllib.quote(nodename)}
        return url

    def get_queue_url(self):
        url = "%(baseurl)s/queue/" % {'baseurl': self.baseurl}
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
        NODE_TYPE   = 'hudson.slaves.DumbSlave$DescriptorImpl'
        MODE = 'NORMAL'
        if self.has_node(name):
            return Node(nodename=name, baseurl=self.get_node_url(nodename=name), jenkins_obj=self)
        if exclusive:
            MODE = 'EXCLUSIVE'
        params = {
            'name' : name,
            'type' : NODE_TYPE,
            'json' : json.dumps ({
                'name'            : name,
                'nodeDescription' : node_description,
                'numExecutors'    : num_executors,
                'remoteFS'        : remote_fs,
                'labelString'     : labels,
                'mode'            : MODE,
                'type'            : NODE_TYPE,
                'retentionStrategy' : { 'stapler-class'  : 'hudson.slaves.RetentionStrategy$Always' },
                'nodeProperties'    : { 'stapler-class-bag' : 'true' },
                'launcher'          : { 'stapler-class' : 'hudson.slaves.JNLPLauncher' }
            })
        }
        url = self.get_node_url() + "doCreateItem?%s" % urllib.urlencode(params)
        self.requester.get_and_confirm_status(url)

        return Node(nodename=name, baseurl=self.get_node_url(nodename=name), jenkins_obj=self)
