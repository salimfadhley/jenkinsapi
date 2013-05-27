from jenkinsapi.exceptions import UnknownJob, NotAuthorized
from jenkinsapi.fingerprint import Fingerprint
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.job import Job
from jenkinsapi.node import Node
from jenkinsapi.queue import Queue
from jenkinsapi.view import View
from jenkinsapi import config
from utils.urlopener import mkurlopener, mkopener, NoAuto302Handler
import cookielib
import logging
import time
import urllib
import urllib2
import urlparse

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
    def __init__(self, baseurl, username=None, password=None, proxyhost=None, proxyport=None, proxyuser=None, proxypass=None, formauth=False, krbauth=False):
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
        JenkinsBase.__init__(self, baseurl, formauth=formauth, krbauth=krbauth)

    def _clone(self):
        return Jenkins(self.baseurl, username=self.username,
                       password=self.password, proxyhost=self.proxyhost,
                       proxyport=self.proxyport, proxyuser=self.proxyuser,
                       proxypass=self.proxypass, formauth=self.formauth, krbauth=self.krbauth)

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

    def get_base_server_url(self):
        return self.baseurl[:-(len(config.JENKINS_API))] 

    def get_opener(self):
        if self.formauth:
            return self.get_login_opener()
        if self.krbauth:
            return self.get_krb_opener()
        return mkurlopener(*self.get_auth())

    def get_login_opener(self):
        hdrs = []
        if getattr(self, '_cookies', False):
            mcj = cookielib.MozillaCookieJar()
            for c in self._cookies:
                mcj.set_cookie(c)
            hdrs.append(urllib2.HTTPCookieProcessor(mcj))
        return mkopener(*hdrs)

    def get_krb_opener(self):
        if not mkkrbopener:
            raise NotImplementedError('JenkinsAPI was installed without Kerberos support.')
        return mkkrbopener(self.baseurl)

    def login(self):
        formdata = dict(j_username=self.username, j_password=self.password,
                        remember_me=True, form='/')
        formdata.update(dict(json=json.dumps(formdata), Submit='log in'))
        formdata = urllib.urlencode(formdata)

        loginurl = urlparse.urljoin(self.baseurl, 'j_acegi_security_check')
        mcj = cookielib.MozillaCookieJar()
        cookiehandler = urllib2.HTTPCookieProcessor(mcj)

        urlopen = mkopener(NoAuto302Handler, cookiehandler)
        res = urlopen(loginurl, data=formdata)
        self._cookies = [c for c in mcj]
        return res.getcode() == 302

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
        headers = {'Content-Type': 'text/xml'}
        qs = urllib.urlencode({'name': jobname})
        url = urlparse.urljoin(self.baseurl, "createItem?%s" % qs)
        request = urllib2.Request(url, config, headers)
        self.post_data(request, None)
        newjk = self._clone()
        return newjk.get_job(jobname)

    def copy_job(self, jobname, newjobname):
        """
        Copy a job
        :param jobname: name of a exist job, str
        :param newjobname: name of new job, str
        :return: new Job obj
        """
        qs = urllib.urlencode({'name': newjobname,
                               'mode': 'copy',
                               'from': jobname})
        copy_job_url = urlparse.urljoin(self.baseurl, "createItem?%s" % qs)
        self.post_data(copy_job_url, '')
        newjk = self._clone()
        return newjk.get_job(newjobname)

    def delete_job(self, jobname):
        """
        Delete a job by name
        :param jobname: name of a exist job, str
        :return: new jenkins_obj
        """
        delete_job_url = urlparse.urljoin(self._clone().get_job(jobname).baseurl, "doDelete" )
        self.post_data(delete_job_url, '')
        newjk = self._clone()
        return newjk

    def rename_job(self, jobname, newjobname):
        """
        Rename a job
        :param jobname: name of a exist job, str
        :param newjobname: name of new job, str
        :return: new Job obj
        """
        qs = urllib.urlencode({'newName': newjobname})
        rename_job_url = urlparse.urljoin(self._clone().get_job(jobname).baseurl, "doRename?%s" % qs)
        self.post_data(rename_job_url, '')
        newjk = self._clone()
        return newjk.get_job(newjobname)

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
        newjk = self._clone()
        return newjk

    def create_view(self, str_view_name, people=None):
        """
        Create a view, viewExistsCheck
        :param str_view_name: name of new view, str
        :return: new view obj
        """
        url = urlparse.urljoin(self.baseurl, "user/%s/my-views/" % people) if people else self.baseurl
        qs = urllib.urlencode({'value': str_view_name})
        viewExistsCheck_url = urlparse.urljoin(url, "viewExistsCheck?%s" % qs)
        fn_urlopen = self.get_jenkins_obj().get_opener()
        try:
            r = fn_urlopen(viewExistsCheck_url).read()
        except urllib2.HTTPError, e:
            log.debug("Error reading %s" % viewExistsCheck_url)
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
                createView_url = urlparse.urljoin(url, "createView")
                result = self.post_data(createView_url, params)
            except urllib2.HTTPError, e:
                log.debug("Error post_data %s" % createView_url)
                log.exception(e)
            return urlparse.urljoin(url, "view/%s/" % str_view_name)

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
