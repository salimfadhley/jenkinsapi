import time
import urllib
import urllib2
import logging
import urlparse
import requests
import StringIO
import cookielib
from utils.urlopener import mkurlopener, mkopener, NoAuto302Handler

from jenkinsapi import config
from jenkinsapi.job import Job
from jenkinsapi.nodes import Nodes
from jenkinsapi.node import Node
from jenkinsapi.queue import Queue
from jenkinsapi.view import View
from jenkinsapi.fingerprint import Fingerprint
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.utils.requester import Requester
from jenkinsapi.exceptions import UnknownJob, NotAuthorized, JenkinsAPIException

try:
    import json
except ImportError:
    import simplejson as json

try:
    # Kerberos is now an extras_require - please see
    # http://pythonhosted.org/distribute/setuptools.html#declaring-extras-optional-features-with-their-own-dependencies
    from utils.urlopener_kerberos import mkkrbopener
except ImportError:
    mkkrbopener = None

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

    def get_base_server_url(self):
        if config.JENKINS_API in self.baseurl:
            return self.baseurl[:-(len(config.JENKINS_API))]
        else:
            return self.baseurl

    def validate_fingerprint(self, id):
        obj_fingerprint = Fingerprint(self.baseurl, id, jenkins_obj=self)
        obj_fingerprint.validate()
        log.info("Jenkins says %s is valid" % id)

    def reload(self):
        '''Try and reload the configuration from disk'''
        try:
            self.requester.get_url("%(baseurl)s/reload" % self.__dict__)
        except urllib2.HTTPError, e:
            if e.code == 403:
                raise NotAuthorized("You are not authorized to reload this server")
            raise

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
            raise JenkinsAPIException('Job %s already exists!' % jobname)

        params = {'name': jobname}
        self.requester.post_xml_and_confirm_status(self.get_create_url(), data=config, params=params)
        self.poll()
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
        response = self.requester.post_and_confirm_status(
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
        response = self.requester.post_and_confirm_status(
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

    def _get_views(self):
        log.debug('_get_views: self._data.has_key[views] %s' % 
                self._data.has_key('views'))
        if not self._data.has_key("views"):
            pass
        else:
            for viewdict in self._data["views"]:
                yield viewdict["name"], viewdict["url"]

    def get_view_dict(self):
        return dict(self._get_views())

    def get_view_url(self, str_view_name):
        try:
            view_dict = self.get_view_dict()
            log.debug('view_dict=%s' % view_dict)
            return view_dict[ str_view_name ]
        except KeyError:
            #noinspection PyUnboundLocalVariable
            all_views = ", ".join(view_dict.keys())
            raise KeyError("View %s is not known - available: %s" % (str_view_name, all_views))

    def get_view(self, str_view_name):
        view_url = self.get_view_url(str_view_name)
        view_api_url = self.python_api_url(view_url)
        return View(view_url , str_view_name, jenkins_obj=self)

    def get_view_by_url(self, str_view_url):
        #for nested view
        str_view_name = str_view_url.split('/view/')[-1].replace('/', '')
        return View(str_view_url , str_view_name, jenkins_obj=self)

    def delete_view_by_url(self, str_url):
        url = "%s/doDelete" % str_url
        response = self.requester.get_url(url, data='')
        self.poll()
        return self

    def get_nodes(self):
        url = self.get_nodes_url()
        return Nodes(url, self)

    def create_view(self, str_view_name, person=None):
        """
        Create a view
        :param str_view_name: name of new view, str
        :param person: Person name (to create personal view), str
        :return: new View obj or None if view was not created
        """
        url = urlparse.urljoin(self.baseurl, "user/%s/my-views/" % person) if person else self.baseurl
        qs = urllib.urlencode({'value': str_view_name})
        viewExistsCheck_url = urlparse.urljoin(url, "viewExistsCheck?%s" % qs)
        log.debug('viewExistsCheck_url=%s' % viewExistsCheck_url)
        result = self.requester.get_url(viewExistsCheck_url)
        log.debug('result=%s' % result)
        # Jenkins returns "<div/>" if view does not exist
        if len(result) > len('<div/>'):
            log.error('A view "%s" already exists' % (str_view_name))
            return None
        else:
            data = {"mode":"hudson.model.ListView", "Submit": "OK"}
            data['name'] = str_view_name
            # data['json'] = data.copy()
            # log.debug('json data=%s' % data)
            # params = urllib.urlencode(data)
            try:
                createView_url = urlparse.urljoin(url, "createView")
                log.debug('createView_url=%s' % createView_url)
                result = self.requester.post_url(createView_url, data)
            except urllib2.HTTPError, e:
                log.debug("Error post_data %s" % createView_url)
                log.exception(e)
            # We changed Jenkins config - need to update ourself
            self.poll()
            new_view_obj = self.get_view(str_view_name)
            assert isinstance(new_view_obj, View)
            return new_view_obj

    def delete_view(self, str_view_name, view=None, person=None):
        """
        Delete a view
        :param str_view_name: name of the view, str
        :param view: View object to be deleted, jenkinsapi.View
        :param person: Person name (to create personal view), str
        :return: True if view has been deleted, False if view does not exist
        """
        url = urlparse.urljoin(self.baseurl, "user/%s/my-views/" % person) if person else self.baseurl
        qs = urllib.urlencode({'value': str_view_name})
        viewExistsCheck_url = urlparse.urljoin(url, "viewExistsCheck?%s" % qs)
        log.debug('viewExistsCheck_url=%s' % viewExistsCheck_url)
        result = self.requester.get_url(viewExistsCheck_url)
        log.debug('result=%s' % result)
        # Jenkins returns "<div/>" if view does not exist
        if len(result) == len('<div/>'):
            log.error('A view the name "%s" does not exist' % (str_view_name))
            return False
        else:
            self.delete_view_by_url(urlparse.urljoin(url, 'view/%s' % str_view_name))
            # We changed Jenkins config - need to update ourself
            self.poll()
            # TODO: add check here that the view actually been deleted
            return True

    def __getitem__(self, jobname):
        """
        Get a job by name
        :param jobname: name of job, str
        :return: Job obj
        """
        for url, name in self.get_jobs_info():
            if name == jobname:
                preferred_scheme = urlparse.urlsplit(self.baseurl).scheme
                url_split = urlparse.urlsplit(url)
                preferred_url = urlparse.urlunsplit([preferred_scheme, url_split.netloc, url_split.path, url_split.query, url_split.fragment])
                return Job(preferred_url, name, jenkins_obj=self)
        raise UnknownJob(jobname)

    def __contains__(self, jobname):
        """
        Does a job by the name specified exist
        :param jobname: string
        :return: boolean
        """
        return jobname in self.get_jobs_list()

    def get_node_dict(self):
        """Get registered slave nodes on this instance"""
        url = self.python_api_url(self.get_node_url())
        node_dict = dict(self.get_data(url))
        return dict(
            (node['displayName'], self.python_api_url(self.get_node_url(node['displayName'])))
                for node in node_dict['computer'])

    def get_node(self, nodename):
        """Get a node object for a specific node"""
        node_url = self.get_node_url(nodename)
        return Node(node_url, nodename, jenkins_obj=self)

    def get_node_url(self, nodename=""):
        """Return the url for nodes"""
        url = "%(baseurl)s/computer/%(nodename)s" % {'baseurl': self.baseurl, 'nodename': urllib.quote(nodename)}
        return url

    def get_queue_url(self):
        url = "%(baseurl)s/queue/" % {'baseurl': self.get_base_server_url()}
        return url

    def get_queue(self):
        queue_url = self.get_queue_url()
        return Queue(queue_url, self)

    def has_node(self, nodename):
        """
        Does a node by the name specified exist
        :param nodename: string, hostname
        :return: boolean
        """
        return nodename in self.get_node_dict()

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
        fn_urlopen = self.get_jenkins_obj().get_opener()
        try:
            fn_urlopen(url).read()
        except urllib2.HTTPError, e:
            log.debug("Error reading %s" % url)
            log.exception(e)
            raise
        return not self.has_node(nodename)

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

        fn_urlopen = self.get_jenkins_obj().get_opener()
        try:
            fn_urlopen(url).read()
        except urllib2.HTTPError, e:
            log.debug("Error reading %s" % url)
            log.exception(e)
            raise
        return Node(nodename=name, baseurl=self.get_node_url(nodename=name), jenkins_obj=self)
