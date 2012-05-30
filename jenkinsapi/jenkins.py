from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.fingerprint import Fingerprint
from jenkinsapi.job import Job
from jenkinsapi.view import View
from jenkinsapi.node import Node
from jenkinsapi.exceptions import UnknownJob, NotAuthorized
from utils.urlopener import mkurlopener
import logging
import time
import urllib2
import urllib
try:
    import json
except ImportError:
    import simplejson as json

log = logging.getLogger(__name__)

class Jenkins(JenkinsBase):
    """
    Represents a jenkins environment.
    """
    def __init__(self, baseurl, username=None, password=None, proxyhost=None, proxyport=None, proxyuser=None, proxypass=None):
        """

        :param baseurl: baseurl for jenkins instance including port, str
        :param username: username for jenkins auth, str
        :param password: password for jenkins auth, str
        :param proxyhost: proxyhostname, str
        :param proxyport: proxyport, int
        :param proxyuser: proxyusername for proxy auth, str
        :param proxypass: proxypassword for proxyauth, str
        :return: a Jenkins obj
        """
        self.username = username
        self.password = password
        self.proxyhost = proxyhost
        self.proxyport = proxyport
        self.proxyuser = proxyuser
        self.proxypass = proxypass
        JenkinsBase.__init__(self, baseurl)

    def get_proxy_auth(self):
        return self.proxyhost, self.proxyport, self.proxyuser, self.proxypass

    def get_jenkins_auth(self):
        return self.username, self.password, self.baseurl

    def get_auth(self):
        auth_args = []
        auth_args.extend(self.get_jenkins_auth())
        auth_args.extend(self.get_proxy_auth())
        log.debug("args: %s" % auth_args)
        return auth_args

    def get_opener(self):
        return mkurlopener(*self.get_auth())

    def validate_fingerprint(self, id):
        obj_fingerprint = Fingerprint(self.baseurl, id, jenkins_obj=self)
        obj_fingerprint.validate()
        log.info("Jenkins says %s is valid" % id)

    def reload(self):
        '''Try and reload the configuration from disk'''
        try:
            self.hit_url("%(baseurl)s/reload" % self.__dict__)
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

    def get_jobs(self):
        """
        Fetch all the build-names on this Jenkins server.
        """
        for info in self._data["jobs"]:
            yield info["name"], Job(info["url"], info["name"], jenkins_obj=self)

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
        return jobname in self.get_jobs_list()

    def copy_job(self, jobname, newjobname):
        """
        Copy a job 
        :param jobname: name of a exist job, str
        :param newjobname: name of new job, str
        :return: new Job obj
        """
        copy_job_url = "%screateItem?name=%s&mode=copy&from=%s" % (self.baseurl, newjobname, jobname)
        self.post_data(copy_job_url, '')
        return Jenkins(self.baseurl).get_job(newjobname)

    def delete_job(self, jobname):
        """
        Delete a job by name
        :param jobname: name of a exist job, str
        :return: new jenkins_obj
        """
        delete_job_url = "%sdoDelete" % Jenkins(self.baseurl).get_job(jobname).baseurl
        self.post_data(delete_job_url, '')
        return Jenkins(self.baseurl)

    def iteritems(self):
        return self.get_jobs()

    def iterkeys(self):
        for info in self._data["jobs"]:
            yield info["name"]

    def keys(self):
        return [ a for a in self.iterkeys() ]

    def __str__(self):
        return "Jenkins server at %s" % self.baseurl

    def _get_views(self):
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
        url = "%s/doDelete" %str_url
        self.post_data(url, '')
        return Jenkins(self.baseurl)

    def create_view(self, str_view_name, people=None):
        """
        Create a view, viewExistsCheck
        :param str_view_name: name of new view, str
        :return: new view obj
        """
        
        if people:
            url = "%s/user/%s/my-views" %(self.baseurl, people)
        else:
            url = self.baseurl
        viewExistsCheck_url = "%s/viewExistsCheck?value=%s" %(url, str_view_name)
        fn_urlopen = self.get_jenkins_obj().get_opener()
        try:
            r = fn_urlopen(viewExistsCheck_url).read()
        except urllib2.HTTPError, e:
            log.debug("Error reading %s" % url)
            log.exception(e)
            raise
        """<div/>"""
        if len(r) > 7: 
            return 'A view already exists with the name "%s"' % (str_view_name)
        else:
            data = {"mode":"hudson.model.ListView", "Submit": "OK"}
            data['name']=str_view_name
            data['json'] = data.copy()
            params = urllib.urlencode(data)
            try:
                result = self.post_data('%s/createView' % url, params)
            except urllib2.HTTPError, e:
                log.debug("Error post_data %s" % url)
                log.exception(e)
            return url

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

    def get_node_dict(self):
        """Get registered slave nodes on this instance"""
        url = self.python_api_url(self.get_node_url())
        node_dict = dict(self.get_data(url))
        return dict(
            (node['displayName'], self.python_api_url(self.get_node_url(node['displayName'])))
                for node in node_dict['computer'])

    def get_node(self, nodename):
        """Get a node object for a specific node"""
        node_url = self.python_api_url(self.get_node_url(nodename))
        return Node(node_url, nodename, jenkins_obj=self)

    def get_node_url(self, nodename=""):
        """Return the url for nodes"""
        url = "%(baseurl)s/computer/%(nodename)s" % {'baseurl': self.baseurl, 'nodename': urllib.quote(nodename)}
        return url

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
        NODE_TYPE   = 'jenkins.slaves.DumbSlave$DescriptorImpl'
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
                'retentionStrategy' : { 'stapler-class'  : 'jenkins.slaves.RetentionStrategy$Always' },
                'nodeProperties'    : { 'stapler-class-bag' : 'true' },
                'launcher'          : { 'stapler-class' : 'jenkins.slaves.JNLPLauncher' }
            })
        }
        url = "%(nodeurl)s/doCreateItem?%(params)s" % {
            'nodeurl': self.get_node_url(),
            'params': urllib.urlencode(params)
        }
        print url
        fn_urlopen = self.get_jenkins_obj().get_opener()
        try:
            fn_urlopen(url).read()
        except urllib2.HTTPError, e:
            log.debug("Error reading %s" % url)
            log.exception(e)
            raise
        return Node(nodename=name, baseurl=self.get_node_url(nodename=name), jenkins_obj=self)
