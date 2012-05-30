from jenkinsapi.artifact import Artifact
from jenkinsapi import config
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.exceptions import NoResults, FailedNoResults
from jenkinsapi.constants import STATUS_FAIL, STATUS_ABORTED, RESULTSTATUS_FAILURE
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

    def id(self):
        return self._data["number"]

    def get_status(self):
        return self._data["result"]

    def get_revision(self):
        maxRevision = 0
        for repoPathSet in self._data["changeSet"]["revisions"]:
            maxRevision = max(repoPathSet["revision"], maxRevision)
        return maxRevision

    def get_duration(self):
        return self._data["duration"]

    def get_artifacts( self ):
        for afinfo in self._data["artifacts"]:
            url = "%sartifact/%s" % ( self.baseurl, afinfo["relativePath"] )
            af = Artifact( afinfo["fileName"], url, self )
            yield af
            del af, url

    def get_artifact_dict(self):
        return dict( (a.filename, a) for a in self.get_artifacts() )

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
        return ( not self.is_running() ) and self._data["result"] == 'SUCCESS'

    def block_until_complete(self, delay=15):
        assert isinstance( delay, int )
        count = 0
        while self.is_running():
            total_wait = delay * count
            log.info("Waited %is for %s #%s to complete" % ( total_wait, self.job.id(), self.id() ) )
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
        if buildstatus in [ STATUS_FAIL, RESULTSTATUS_FAILURE, STATUS_ABORTED ]:
            raise FailedNoResults( self.STR_TPL_NOTESTS_ERR % ( str(self), buildstatus ) )
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
            all_actions.update( dct_action )
        return all_actions

    def get_timestamp(self):
        return self._data['timestamp']
