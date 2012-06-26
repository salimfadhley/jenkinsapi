import logging
import urlparse
import urllib2
import urllib
from bs4 import BeautifulSoup
from collections import defaultdict
from time import sleep
from jenkinsapi.build import Build
from jenkinsapi.jenkinsbase import JenkinsBase

from exceptions import NoBuildData, NotFound

log = logging.getLogger(__name__)

class Job(JenkinsBase):
    """
    Represents a jenkins job
    A job can hold N builds which are the actual execution environments
    """
    def __init__( self, url, name, jenkins_obj ):
        self.name = name
        self.jenkins = jenkins_obj
        self._revmap = None
        self._config = None
        JenkinsBase.__init__( self, url )

    def id( self ):
        return self._data["name"]

    def __str__(self):
        return self._data["name"]

    def get_jenkins_obj(self):
        return self.jenkins

    def get_build_triggerurl( self, token=None, params={} ):
        if token is None and not params:
            extra = "build"
        elif params:
            if token:
                assert isinstance(token, str ), "token if provided should be a string."
                params['token'] = token
            extra = "buildWithParameters?" + urllib.urlencode(params)
        else:
            assert isinstance(token, str ), "token if provided should be a string."
            extra = "build?" + urllib.urlencode({'token':token})
        buildurl = urlparse.urljoin( self.baseurl, extra )
        return buildurl

    def invoke(self, securitytoken=None, block=False, skip_if_running=False, invoke_pre_check_delay=3, invoke_block_delay=15, params={}):
        assert isinstance( invoke_pre_check_delay, (int, float) )
        assert isinstance( invoke_block_delay, (int, float) )
        assert isinstance( block, bool )
        assert isinstance( skip_if_running, bool )
        if self.is_queued():
            log.warn( "Will not request new build because %s is already queued" % self.id() )
            pass
        elif self.is_running():
            if skip_if_running:
                log.warn( "Will not request new build because %s is already running" % self.id() )
                pass
            else:
                log.warn("Will re-schedule %s even though it is already running" % self.id() )
        original_build_no = self.get_last_buildnumber()
        log.info( "Attempting to start %s on %s" % ( self.id(), repr(self.get_jenkins_obj()) ) )
        url = self.get_build_triggerurl( securitytoken, params)
        html_result = self.hit_url(url)
        assert len( html_result ) > 0
        if invoke_pre_check_delay > 0:
            log.info("Waiting for %is to allow Jenkins to catch up" % invoke_pre_check_delay )
            sleep( invoke_pre_check_delay )
        if block:
            total_wait = 0
            while self.is_queued():
                log.info( "Waited %is for %s to begin..." % ( total_wait, self.id() ) )
                sleep( invoke_block_delay )
                total_wait += invoke_block_delay
            if self.is_running():
                running_build = self.get_last_build()
                running_build.block_until_complete( delay=invoke_pre_check_delay )
            assert self.get_last_buildnumber() > original_build_no, "Job does not appear to have run."
        else:
            if self.is_queued():
                log.info( "%s has been queued." % self.id() )
            elif self.is_running():
                log.info( "%s is running." % self.id() )
            elif original_build_no < self.get_last_buildnumber():
                log.info( "%s has completed." % self.id() )
            else:
                raise AssertionError("The job did not schedule.")

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
        bn = self.get_last_buildnumber()
        return self.get_build( bn )

    def get_last_build_or_none(self):
        """
        Get the last build or None if there is no builds
        """
        bn = self.get_last_buildnumber()
        if bn is not None:
            return self.get_build(bn)

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
        if self.get_vcs() == 'svn' and not isinstance(revision, int):
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
            log.info("No build info available for %s, assuming not running." % str(self) )
        return False

    def get_config(self):
        '''Returns the config.xml from the job'''
        return self.hit_url("%(baseurl)s/config.xml" % self.__dict__)

    def load_config(self):
        self._config = self.get_config()

    def get_vcs(self):
        if self._config is None:
            self.load_config()

        bs = BeautifulSoup(self._config, 'xml')
        vcsmap = {
            'hudson.scm.SubversionSCM': 'svn',
            'hudson.plugins.git.GitSCM': 'git',
            'hudson.plugins.mercurial.MercurialSCM': 'hg',
            }
        return vcsmap.get(bs.project.scm.attrs['class'])

    def update_config(self, config):
        '''Update the config.xml to the job'''
        return self.post_data("%(baseurl)s/config.xml" % self.__dict__, config)

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
