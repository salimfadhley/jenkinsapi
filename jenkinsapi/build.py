import time
import urlparse
import urllib2
import datetime
from jenkinsapi.artifact import Artifact
from jenkinsapi import config
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.exceptions import NoResults
from jenkinsapi.constants import STATUS_SUCCESS
from jenkinsapi.result_set import ResultSet

from time import sleep
import logging

log = logging.getLogger(__name__)

class Build(JenkinsBase):
    """
    Represents a jenkins build, executed in context of a job.
    """

    STR_TOTALCOUNT = "totalCount"
    STR_TPL_NOTESTS_ERR = "%s has status %s, and does not have any test results"

    def __init__( self, url, buildno, job ):
        assert type(buildno) == int
        self.buildno = buildno
        self.job = job
        JenkinsBase.__init__( self, url )

    def __str__(self):
        return self._data['fullDisplayName']

    @property
    def name(self):
        return str(self)

    def get_number(self):
        return self._data["number"]

    def get_status(self):
        return self._data["result"]

    def get_revision(self):
        vcs = self._data['changeSet']['kind'] or 'git'
        return getattr(self, '_get_%s_rev' % vcs, lambda: None)()

    def _get_svn_rev(self):
        maxRevision = 0
        for repoPathSet in self._data["changeSet"]["revisions"]:
            maxRevision = max(repoPathSet["revision"], maxRevision)
        return maxRevision

    def _get_git_rev(self):
        for item in self._data['actions']:
            branch = item.get('buildsByBranchName')
            head = branch and branch.get('origin/HEAD')
            if head:
                return head['revision']['SHA1']

    def _get_hg_rev(self):
        return [x['mercurialNodeName'] for x in self._data['actions'] if 'mercurialNodeName' in x][0]

    def get_duration(self):
        return self._data["duration"]

    def get_artifacts( self ):
        for afinfo in self._data["artifacts"]:
            url = "%sartifact/%s" % ( self.baseurl, afinfo["relativePath"] )
            af = Artifact( afinfo["fileName"], url, self )
            yield af
            del af, url

    def get_artifact_dict(self):
        return dict( (a.url[len(a.build.baseurl + "artifact/"):], a) for a in self.get_artifacts() )

    def get_upstream_job_name(self):
        """
        Get the upstream job name if it exist, None otherwise
        :return: String or None
        """
        try:
            return self.get_actions()['causes'][0]['upstreamProject']
        except KeyError:
            return None

    def get_upstream_job(self):
        """
        Get the upstream job object if it exist, None otherwise
        :return: Job or None
        """
        if self.get_upstream_job_name():
            return self.get_jenkins_obj().get_job(self.get_upstream_job_name())
        else:
            return None

    def get_upstream_build_number(self):
        """
        Get the upstream build number if it exist, None otherwise
        :return: int or None
        """
        try:
            return int(self.get_actions()['causes'][0]['upstreamBuild'])
        except KeyError:
            return None

    def get_upstream_build(self):
        """
        Get the upstream build if it exist, None otherwise
        :return Build or None
        """
        upstream_job = self.get_upstream_job()
        if upstream_job:
            return upstream_job.get_build(self.get_upstream_build_number())
        else:
            return None

    def get_master_job_name(self):
        """
        Get the master job name if it exist, None otherwise
        :return: String or None
        """
        try:
            return self.get_actions()['parameters'][0]['value']
        except KeyError:
            return None

    def get_master_job(self):
        """
        Get the master job object if it exist, None otherwise
        :return: Job or None
        """
        if self.get_master_job_name():
            return self.get_jenkins_obj().get_job(self.get_master_job_name())
        else:
            return None

    def get_master_build_number(self):
        """
        Get the master build number if it exist, None otherwise
        :return: int or None
        """
        try:
            return int(self.get_actions()['parameters'][1]['value'])
        except KeyError:
            return None

    def get_master_build(self):
        """
        Get the master build if it exist, None otherwise
        :return Build or None
        """
        master_job = self.get_master_job()
        if master_job:
            return master_job.get_build(self.get_master_build_number())
        else:
            return None

    def get_downstream_jobs(self):
        """
        Get the downstream jobs for this build
        :return List of jobs or None
        """
        downstream_jobs_names = self.job.get_downstream_job_names()
        fingerprint_data = self.get_data("%s?depth=2&tree=fingerprint[usage[name]]" % self.python_api_url(self.baseurl))
        downstream_jobs = []
        try:
            fingerprints = fingerprint_data['fingerprint'][0]
            for f in fingerprints['usage']:
                if f['name'] in downstream_jobs_names:
                    downstream_jobs.append(self.get_jenkins_obj().get_job(f['name']))
            return downstream_jobs
        except (IndexError, KeyError):
            return None

    def get_downstream_job_names(self):
        """
        Get the downstream job names for this build
        :return List of string or None
        """
        downstream_jobs_names = self.job.get_downstream_job_names()
        fingerprint_data = self.get_data("%s?depth=2&tree=fingerprint[usage[name]]" % self.python_api_url(self.baseurl))
        downstream_names = []
        try:
            fingerprints = fingerprint_data['fingerprint'][0]
            for f in fingerprints['usage']:
                if f['name'] in downstream_jobs_names:
                    downstream_names.append(f['name'])
            return downstream_names
        except (IndexError, KeyError):
            return None

    def get_downstream_builds(self):
        """
        Get the downstream builds for this build
        :return List of Build or None
        """
        downstream_jobs_names = self.job.get_downstream_job_names()
        fingerprint_data = self.get_data("%s?depth=2&tree=fingerprint[usage[name,ranges[ranges[end,start]]]]" % self.python_api_url(self.baseurl))
        downstream_builds = []
        try:
            fingerprints = fingerprint_data['fingerprint'][0]
            for f in fingerprints['usage']:
                if f['name'] in downstream_jobs_names:
                    downstream_builds.append(self.get_jenkins_obj().get_job(f['name']).get_build(f['ranges']['ranges'][0]['start']))
            return downstream_builds
        except (IndexError, KeyError):
            return None

    def is_running( self ):
        """
        Return a bool if running.
        """
        self.poll()
        return self._data["building"]

    def is_good( self ):
        """
        Return a bool, true if the build was good.
        If the build is still running, return False.
        """
        return ( not self.is_running() ) and self._data["result"] == STATUS_SUCCESS

    def block_until_complete(self, delay=15):
        assert isinstance( delay, int )
        count = 0
        while self.is_running():
            total_wait = delay * count
            log.info("Waited %is for %s #%s to complete" % ( total_wait, self.job.name, self.name ) )
            sleep( delay )
            count += 1

    def get_jenkins_obj(self):
        return self.job.get_jenkins_obj()

    def get_result_url(self):
        """
        Return the URL for the object which provides the job's result summary.
        """
        url_tpl = r"%stestReport/%s"
        return  url_tpl % ( self._data["url"] , config.JENKINS_API )

    def get_resultset(self):
        """
        Obtain detailed results for this build.
        """
        result_url = self.get_result_url()
        if self.STR_TOTALCOUNT not in self.get_actions():
            raise NoResults( "%s does not have any published results" % str(self) )
        buildstatus = self.get_status()
        if not self.get_actions()[self.STR_TOTALCOUNT]:
            raise NoResults( self.STR_TPL_NOTESTS_ERR % ( str(self), buildstatus ) )
        obj_results = ResultSet( result_url, build=self )
        return obj_results

    def has_resultset(self):
        """
        Return a boolean, true if a result set is available. false if not.
        """
        return self.STR_TOTALCOUNT in self.get_actions()

    def get_actions(self):
        all_actions = {}
        for dct_action in self._data["actions"]:
            if dct_action is None: continue
            all_actions.update( dct_action )
        return all_actions

    def get_timestamp(self):
        # Java timestamps are given in miliseconds since the epoch start!
        return datetime.datetime(*time.localtime(self._data['timestamp']/1000.0)[:6])

    def stop(self):
        """
        Stops the build execution if it's running
        :return boolean True if succeded False otherwise or the build is not running
        """
        if not self.is_running():
            return False

        stopbuildurl = urlparse.urljoin(self.baseurl, 'stop')
        try:
            self.post_data(stopbuildurl, '')
        except urllib2.HTTPError:
            # The request doesn't have a response, so it returns 404,
            # it's the expected behaviour
            pass
        return True
