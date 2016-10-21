"""
Module for jenkinsapi Jenkins object
"""
try:
    import urlparse
    from urllib import quote as urlquote
except ImportError:
    # Python3
    import urllib.parse as urlparse
    from urllib.parse import quote as urlquote

import logging

from jenkinsapi import config
from jenkinsapi.credentials import Credentials
from jenkinsapi.credentials import Credentials2x
from jenkinsapi.executors import Executors
from jenkinsapi.jobs import Jobs
from jenkinsapi.view import View
from jenkinsapi.label import Label
from jenkinsapi.nodes import Nodes
from jenkinsapi.plugins import Plugins
from jenkinsapi.views import Views
from jenkinsapi.queue import Queue
from jenkinsapi.fingerprint import Fingerprint
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.utils.requester import Requester
from jenkinsapi.custom_exceptions import JenkinsAPIException

log = logging.getLogger(__name__)


class Jenkins(JenkinsBase):

    """
    Represents a jenkins environment.
    """

    def __init__(
            self, baseurl,
            username=None, password=None,
            requester=None, lazy=False,
            ssl_verify=True):
        """
        :param baseurl: baseurl for jenkins instance including port, str
        :param username: username for jenkins auth, str
        :param password: password for jenkins auth, str
        :return: a Jenkins obj
        """
        self.username = username
        self.password = password
        self.requester = requester or Requester(
            username,
            password,
            baseurl=baseurl,
            ssl_verify=ssl_verify)
        self.lazy = lazy
        self.jobs_container = None
        JenkinsBase.__init__(self, baseurl, poll=not lazy)

    def _poll(self, tree=None):
        url = self.python_api_url(self.baseurl)
        return self.get_data(url, tree='jobs[name,color,url]'
                             if not tree else tree)

    def _poll_if_needed(self):
        if self.lazy and self._data is None:
            self.poll()

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
        if self.jobs_container is None:
            self.jobs_container = Jobs(self)

        return self.jobs_container

    def get_jobs(self):
        """
        Fetch all the build-names on this Jenkins server.
        """
        return self.jobs.iteritems()

    def get_jobs_info(self):
        """
        Get the jobs information
        :return url, name
        """
        for name, job in self.jobs.iteritems():
            yield job.url, name

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

    def create_job(self, jobname, xml):
        """
        Create a job

        alternatively you can create job using Jobs object:
        self.jobs['job_name'] = config
        :param jobname: name of new job, str
        :param config: configuration of new job, xml
        :return: new Job obj
        """
        return self.jobs.create(jobname, xml)

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

    def items(self):
        """
        :param return: A list of pairs.
            Each pair will be (job name, Job object)
        """
        return list(self.iteritems())

    def get_jobs_list(self):
        return self.jobs.keys()

    def iterkeys(self):
        return self.jobs.iterkeys()

    def iteritems(self):
        return self.jobs.iteritems()

    def keys(self):
        return self.jobs.keys()

    def __str__(self):
        return "Jenkins server at %s" % self.baseurl

    @property
    def views(self):
        return Views(self)

    def get_view_by_url(self, str_view_url):
        # for nested view
        str_view_name = str_view_url.split('/view/')[-1].replace('/', '')
        return View(str_view_url, str_view_name, jenkins_obj=self)

    def delete_view_by_url(self, str_url):
        url = "%s/doDelete" % str_url
        self.requester.post_and_confirm_status(url, data='')
        self.poll()
        return self

    def get_label(self, label_name):
        label_url = '%s/label/%s' % (self.baseurl, label_name)
        return Label(label_url, label_name, jenkins_obj=self)

    def __getitem__(self, jobname):
        """
        Get a job by name
        :param jobname: name of job, str
        :return: Job obj
        """
        return self.jobs[jobname]

    def __len__(self):
        return len(self.jobs)

    def __contains__(self, jobname):
        """
        Does a job by the name specified exist
        :param jobname: string
        :return: boolean
        """
        return jobname in self.jobs

    def __delitem__(self, job_name):
        del self.jobs[job_name]

    def get_node(self, nodename):
        """Get a node object for a specific node"""
        return self.get_nodes()[nodename]

    def get_node_url(self, nodename=""):
        """Return the url for nodes"""
        url = urlparse.urljoin(
            self.base_server_url(),
            'computer/%s' %
            urlquote(nodename))
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

    @property
    def nodes(self):
        return self.get_nodes()

    def has_node(self, nodename):
        """
        Does a node by the name specified exist
        :param nodename: string, hostname
        :return: boolean
        """
        self.poll()
        return nodename in self.nodes

    def delete_node(self, nodename):
        """
        Remove a node from the managed slave list
        Please note that you cannot remove the master node

        :param nodename: string holding a hostname
        :return: None
        """
        assert self.has_node(nodename), \
            "This node: %s is not registered as a slave" % nodename
        assert nodename != "master", "you cannot delete the master node"
        del self.nodes[nodename]

    def create_node(self, name, num_executors=2, node_description=None,
                    remote_fs='/var/lib/jenkins',
                    labels=None, exclusive=False):
        """
        Create a new JNLP slave node by name.

        To create SSH node, please see description in Node class

        :param name: fqdn of slave, str
        :param num_executors: number of executors, int
        :param node_description: a freetext field describing the node
        :param remote_fs: jenkins path, str
        :param labels: labels to associate with slave, str
        :param exclusive: tied to specific job, boolean
        :return: node obj
        """
        node_dict = {
            'num_executors': num_executors,
            'node_description': node_description,
            'remote_fs': remote_fs,
            'labels': labels,
            'exclusive': exclusive
        }
        return self.nodes.create_node(name, node_dict)

    def get_plugins_url(self, depth):
        # This only ever needs to work on the base object
        return '%s/pluginManager/api/python?depth=%i' % (self.baseurl, depth)

    def install_plugin(self, plugin):
        plugin = str(plugin)
        if '@' not in plugin or len(plugin.split('@')) != 2:
            usage_err = ('argument must be a string like '
                         '"plugin-name@version", not "{0}"')
            usage_err = usage_err.format(plugin)
            raise ValueError(usage_err)
        payload = '<jenkins> <install plugin="{0}" /> </jenkins>'
        payload = payload.format(plugin)
        url = '%s/pluginManager/installNecessaryPlugins' % (self.baseurl,)
        return self.requester.post_xml_and_confirm_status(
            url, data=payload)

    def install_plugins(self, plugin_list, restart=False):
        for plugin in plugin_list:
            self.install_plugin(plugin)
        if restart:
            self.safe_restart()

    def safe_restart(self):
        """ restarts jenkins when no jobs are running """
        # NB: unlike other methods, the value of resp.status_code
        # here can be 503 even when everything is normal
        url = '%s/safeRestart' % (self.baseurl,)
        valid = self.requester.VALID_STATUS_CODES + [503]
        resp = self.requester.post_and_confirm_status(url, data='',
                                                      valid=valid)
        return resp

    @property
    def plugins(self):
        return self.get_plugins()

    def get_plugins(self, depth=1):
        url = self.get_plugins_url(depth=depth)
        return Plugins(url, self)

    def has_plugin(self, plugin_name):
        return plugin_name in self.plugins

    def get_executors(self, nodename):
        url = '%s/computer/%s' % (self.baseurl, nodename)
        return Executors(url, nodename, self)

    def get_master_data(self):
        url = '%s/computer/api/python' % self.baseurl
        return self.get_data(url)

    @property
    def version(self):
        """
        Return version number of Jenkins
        """
        response = self.requester.get_and_confirm_status(self.baseurl)
        version_key = 'X-Jenkins'
        return response.headers.get(version_key, '0.0')

    def get_credentials(self):
        """
        Return credentials
        """

        if 'credentials' not in self.plugins:
            raise JenkinsAPIException('Credentials plugin not installed')

        if int(self.plugins['credentials'].version[0:1]) == 1:
            url = '%s/credential-store/domain/_/' % self.baseurl
            return Credentials(url, self)
        else:
            url = '%s/credentials/store/system/domain/_/' % self.baseurl
            return Credentials2x(url, self)

    @property
    def credentials(self):
        return self.get_credentials()

    def shutdown(self):
        url = "%s/exit" % self.baseurl
        self.requester.post_and_confirm_status(url, data='')
