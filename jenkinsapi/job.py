import logging
import urlparse
import urllib2
import urllib
import xml.etree.ElementTree as ET
from collections import defaultdict
from time import sleep
from jenkinsapi.build import Build
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi import exceptions
from jenkinsapi.mutable_jenkins_thing import MutableJenkinsThing

from jenkinsapi.exceptions import NoBuildData, NotFound, NotInQueue, WillNotBuild

log = logging.getLogger(__name__)

class Job(JenkinsBase, MutableJenkinsThing):
    """
    Represents a jenkins job
    A job can hold N builds which are the actual execution environments
    """
    def __init__( self, url, name, jenkins_obj ):
        self.name = name
        self.jenkins = jenkins_obj
        self._revmap = None
        self._config = None
        self._element_tree = None
        self._scm_map = {
            'hudson.scm.SubversionSCM': 'svn',
            'hudson.plugins.git.GitSCM': 'git',
            'hudson.plugins.mercurial.MercurialSCM': 'hg',
            'hudson.scm.NullSCM': 'NullSCM'
            }
        self._scmurlmap = {
            'svn' : lambda element_tree: [element for element in element_tree.findall('./scm/locations/hudson.scm.SubversionSCM_-ModuleLocation/remote')],
            'git' : lambda element_tree: [element for element in element_tree.findall('./scm/userRemoteConfigs/hudson.plugins.git.UserRemoteConfig/url')],
            'hg' : lambda element_tree: [element_tree.find('./scm/source')],
            None : lambda element_tree: []
            }
        self._scmbranchmap = {
            'svn' : lambda element_tree: [],
            'git' : lambda element_tree: [element for element in element_tree.findall('./scm/branches/hudson.plugins.git.BranchSpec/name')],
            'hg' : lambda  element_tree: [element_tree.find('./scm/branch')],
            None : lambda element_tree: []
            }
        JenkinsBase.__init__( self, url )

    def __str__(self):
        return self._data["name"]

    def get_description(self):
        return self._data["description"]

    def get_jenkins_obj(self):
        return self.jenkins

    def _get_config_element_tree(self):
        """
        The ElementTree objects creation is unnecessary, it can be a singleton per job
        """
        if self._config is None:
            self.load_config()

        if self._element_tree is None:
            self._element_tree = ET.fromstring(self._config)
        return self._element_tree

    def get_build_triggerurl(self):
        return "%s/build" % self.baseurl

    def invoke(self, securitytoken=None, block=False, skip_if_running=False, invoke_pre_check_delay=3, invoke_block_delay=15, params=None, cause=None):
        assert isinstance( invoke_pre_check_delay, (int, float) )
        assert isinstance( invoke_block_delay, (int, float) )
        assert isinstance( block, bool )
        assert isinstance( skip_if_running, bool )

        # Either copy the params dict or make a new one.
        params = params and dict(params.items()) or {}

        if self.is_queued():
            raise WillNotBuild('%s is already queued' % repr(self))

        elif self.is_running():
            if skip_if_running:
                log.warn( "Will not request new build because %s is already running", self.name )
            else:
                log.warn("Will re-schedule %s even though it is already running", self.name )
        original_build_no = self.get_last_buildnumber()
        log.info( "Attempting to start %s on %s", self.name, repr(self.get_jenkins_obj()) )

        url  = self.get_build_triggerurl()

        if cause:
            params['cause'] = cause

        if securitytoken:
            params['securitytoken'] = securitytoken

        response = self.jenkins.requester.post_url(url, params, data='')

        assert len( response.text ) > 0
        if invoke_pre_check_delay > 0:
            log.info("Waiting for %is to allow Jenkins to catch up" , invoke_pre_check_delay )
            sleep( invoke_pre_check_delay )
        if block:
            total_wait = 0
            while self.is_queued():
                log.info( "Waited %is for %s to begin...", total_wait, self.name  )
                sleep( invoke_block_delay )
                total_wait += invoke_block_delay
            if self.is_running():
                running_build = self.get_last_build()
                running_build.block_until_complete( delay=invoke_pre_check_delay )
            assert self.get_last_buildnumber() > original_build_no, "Job does not appear to have run."
        else:
            if self.is_queued():
                log.info( "%s has been queued.", self.name )
            elif self.is_running():
                log.info( "%s is running.", self.name )
            elif original_build_no < self.get_last_buildnumber():
                log.info( "%s has completed.", self.name )
            elif not response.ok :
                response.raise_for_status()
            else:
                raise AssertionError("The job did not schedule. REASON:%s" % response.reason)

    def _buildid_for_type(self, buildtype):
        """Gets a buildid for a given type of build"""
        KNOWNBUILDTYPES=["lastSuccessfulBuild", "lastBuild", "lastCompletedBuild"]
        assert buildtype in KNOWNBUILDTYPES
        if self._data[buildtype] == None:
            return None
        buildid = self._data[buildtype]["number"]
        assert type(buildid) == int, "Build ID should be an integer, got %s" % repr( buildid )
        return buildid

    def get_last_good_buildnumber( self ):
        """
        Get the numerical ID of the last good build.
        """
        return self._buildid_for_type(buildtype="lastSuccessfulBuild")

    def get_last_buildnumber( self ):
        """
        Get the numerical ID of the last build.
        """
        return self._buildid_for_type(buildtype="lastBuild")

    def get_last_completed_buildnumber( self ):
        """
        Get the numerical ID of the last complete build.
        """
        return self._buildid_for_type(buildtype="lastCompletedBuild")

    def get_build_dict(self):
        if not self._data.has_key( "builds" ):
            raise NoBuildData( repr(self) )
        return dict( ( a["number"], a["url"] ) for a in self._data["builds"] )

    def get_revision_dict(self):
        """
        Get dictionary of all revisions with a list of buildnumbers (int) that used that particular revision
        """
        revs = defaultdict(list)
        if 'builds' not in self._data:
            raise NoBuildData( repr(self))
        for buildnumber in self.get_build_ids():
            revs[self.get_build(buildnumber).get_revision()].append(buildnumber)
        return revs

    def get_build_ids(self):
        """
        Return a sorted list of all good builds as ints.
        """
        return reversed( sorted( self.get_build_dict().keys() ) )

    def get_next_build_number(self):
        """
        Return the next build number that Jenkins will assign.
        """
        return self._data.get('nextBuildNumber', 0)

    def get_last_good_build( self ):
        """
        Get the last good build
        """
        bn = self.get_last_good_buildnumber()
        return self.get_build( bn )

    def get_last_build( self ):
        """
        Get the last build
        """
        buildinfo = self._data["lastBuild"]
        return Build( buildinfo["url"], buildinfo["number"], job=self )


    def get_last_build_or_none(self):
        """
        Get the last build or None if there is no builds
        """
        bn = self.get_last_buildnumber()
        if bn is not None:
            return self.get_last_build()

    def get_last_completed_build( self ):
        """
        Get the last build regardless of status
        """
        bn = self.get_last_completed_buildnumber()
        return self.get_build( bn )

    def get_buildnumber_for_revision(self, revision, refresh=False):
        """

        :param revision: subversion revision to look for, int
        :param refresh: boolean, whether or not to refresh the revision -> buildnumber map
        :return: list of buildnumbers, [int]
        """
        if self.get_scm_type() == 'svn' and not isinstance(revision, int):
            revision = int(revision)
        if self._revmap is None or refresh:
            self._revmap = self.get_revision_dict()
        try:
            return self._revmap[revision]
        except KeyError:
            raise NotFound("Couldn't find a build with that revision")

    def get_build( self, buildnumber ):
        assert type(buildnumber) == int
        url = self.get_build_dict()[ buildnumber ]
        return Build( url, buildnumber, job=self )

    def __getitem__( self, buildnumber ):
        return self.get_build(buildnumber)

    def is_queued_or_running(self):
        return self.is_queued() or self.is_running()

    def is_queued(self):
        self.poll()
        return self._data["inQueue"]

    def is_running(self):
        self.poll()
        try:
            build = self.get_last_build_or_none()
            if build is not None:
                return build.is_running()
        except NoBuildData:
            log.info("No build info available for %s, assuming not running.", str(self) )
        return False

    def get_config(self):
        '''Returns the config.xml from the job'''
        response = self.jenkins.requester.get_and_confirm_status("%(baseurl)s/config.xml" % self.__dict__)
        return response.text

    def load_config(self):
        self._config = self.get_config()

    def get_scm_type(self):
        element_tree = self._get_config_element_tree()
        scm_class = element_tree.find('scm').get('class')
        scm = self._scm_map.get(scm_class)
        if not scm:
            raise exceptions.NotSupportSCM("SCM class \"%s\" not supported by API, job \"%s\"" % (scm_class, self.name))
        if scm == 'NullSCM':
            raise exceptions.NotConfiguredSCM("SCM does not configured, job \"%s\"" % self.name)
        return scm

    def get_scm_url(self):
        """
        Get list of project SCM urls
        For some SCM's jenkins allow to configure and use number of SCM url's
        : return: list of SCM urls
        """
        element_tree = self._get_config_element_tree()
        scm = self.get_scm_type()
        scm_url_list = [scm_url.text for scm_url in self._scmurlmap[scm](element_tree)]
        return scm_url_list

    def get_scm_branch(self):
        """
        Get list of SCM branches
        : return: list of SCM branches
        """
        element_tree = self._get_config_element_tree()
        scm = self.get_scm_type()
        return [scm_branch.text for scm_branch in self._scmbranchmap[scm](element_tree)]

    def modify_scm_branch(self, new_branch, old_branch=None):
        """
        Modify SCM ("Source Code Management") branch name for configured job.
        :param new_branch : new repository branch name to set.
                            If job has multiple branches configured and "old_branch"
                            not provided - method will allways modify first url.
        :param old_branch (optional): exact value of branch name to be replaced.
                            For some SCM's jenkins allow set multiple branches per job
                            this parameter intended to indicate which branch need to be modified
        """
        element_tree = self._get_config_element_tree()
        scm = self.get_scm_type()
        scm_branch_list = self._scmbranchmap[scm](element_tree)
        if scm_branch_list and not old_branch:
            scm_branch_list[0].text = new_branch
            self.update_config(ET.tostring(element_tree))
        else:
            for scm_branch in scm_branch_list:
                if scm_branch.text == old_branch:
                    scm_branch.text = new_branch
                    self.update_config(ET.tostring(element_tree))


    def modify_scm_url(self, new_source_url, old_source_url=None):
        """
        Modify SCM ("Source Code Management") url for configured job.
        :param new_source_url : new repository url to set.
                                If job has multiple repositories configured and "old_source_url"
                                not provided - method will allways modify first url.
        :param old_source_url (optional): for some SCM's jenkins allow set multiple repositories per job
                                this parameter intended to indicate which repository need to be modified
        """
        element_tree = self._get_config_element_tree()
        scm = self.get_scm_type()
        scm_url_list = self._scmurlmap[scm](element_tree)
        if scm_url_list and not old_source_url:
            scm_url_list[0].text = new_source_url
            self.update_config(ET.tostring(element_tree))
        else:
            for scm_url in scm_url_list:
                if scm_url.text == old_source_url:
                    scm_url.text = new_source_url
                    self.update_config(ET.tostring(element_tree))

    def get_config_xml_url(self):
        return '%s/config.xml' % self.baseurl

    def update_config(self, config):
        """
        Update the config.xml to the job
        Also refresh the ElementTree object since the config has changed
        """
        url = self.get_config_xml_url()
        response = self.jenkins.requester.post_url(url, params={}, data='')
        self._element_tree = ET.fromstring(config)
        return response.text

    def get_downstream_jobs(self):
        """
        Get all the possible downstream jobs
        :return List of Job
        """
        downstream_jobs = []
        try:
            for j in self._data['downstreamProjects']:
                downstream_jobs.append(self.get_jenkins_obj().get_job(j['name']))
        except KeyError:
            return []
        return downstream_jobs

    def get_downstream_job_names(self):
        """
        Get all the possible downstream job names
        :return List of String
        """
        downstream_jobs = []
        try:
            for j in self._data['downstreamProjects']:
                downstream_jobs.append(j['name'])
        except KeyError:
            return []
        return downstream_jobs

    def get_upstream_job_names(self):
        """
        Get all the possible upstream job names
        :return List of String
        """
        upstream_jobs = []
        try:
            for j in self._data['upstreamProjects']:
                upstream_jobs.append(j['name'])
        except KeyError:
            return []
        return upstream_jobs

    def get_upstream_jobs(self):
        """
        Get all the possible upstream jobs
        :return List of Job
        """
        upstream_jobs = []
        try:
            for j in self._data['upstreamProjects']:
                upstream_jobs.append(self.get_jenkins_obj().get_job(j['name']))
        except KeyError:
            return []
        return upstream_jobs

    def disable(self):
        '''Disable job'''
        disableurl = urlparse.urljoin(self.baseurl, 'disable' )
        return self.post_data(disableurl, '')

    def enable(self):
        '''Enable job'''
        enableurl = urlparse.urljoin(self.baseurl, 'enable' )
        return self.post_data(enableurl, '')

    def delete_from_queue(self):
        """
        Delete a job from the queue only if it's enqueued
        :raise NotInQueue if the job is not in the queue
        """
        if not self.is_queued():
            raise NotInQueue()
        queue_id = self._data['queueItem']['id']
        cancelurl = urlparse.urljoin(self.get_jenkins_obj().get_queue().baseurl,
                                     'cancelItem?id=%s' % queue_id)
        try:
            self.post_data(cancelurl, '')
        except urllib2.HTTPError:
            # The request doesn't have a response, so it returns 404,
            # it's the expected behaviour
            pass
        return True

    def get_params(self):
        """
        Get the parameters for this job. Format varies by parameter type. Here
        is an example string parameter:
            {
                'type': 'StringParameterDefinition',
                'description': 'Parameter description',
                'defaultParameterValue': {'value': 'default value'},
                'name': 'FOO_BAR'
            }
        """
        for action in self._data['actions']:
            try:
                for param in action['parameterDefinitions']:
                    yield param
            except KeyError:
                continue

    def get_params_list(self):
        """
        Gets the list of parameter names for this job.
        """
        params = []
        for param in self.get_params():
            params.append(param['name'])
        return params
