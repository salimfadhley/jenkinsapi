"""
A jenkins build represents a single execution of a Jenkins Job.

Builds can be thought of as the second level of the jenkins heirarchy
beneath Jobs. Builds can have state, such as whether they are running or
not. They can also have outcomes, such as wether they passed or failed.

Build objects can be associated with Results and Artifacts.g
"""

import time
import logging
import warnings
import datetime

from time import sleep
import pytz
from jenkinsapi import config
from jenkinsapi.artifact import Artifact
from jenkinsapi.result_set import ResultSet
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.constants import STATUS_SUCCESS
from jenkinsapi.custom_exceptions import NoResults
from jenkinsapi.custom_exceptions import JenkinsAPIException

from six.moves.urllib.parse import quote
from requests import HTTPError


log = logging.getLogger(__name__)


class Build(JenkinsBase):

    """
    Represents a jenkins build, executed in context of a job.
    """

    STR_TOTALCOUNT = "totalCount"
    STR_TPL_NOTESTS_ERR = ("%s has status %s, and does not have "
                           "any test results")

    def __init__(self, url, buildno, job, depth=1):
        """
        depth=1 is for backward compatibility consideration

        About depth, the deeper it is, the more build data you get back. If
        depth=0 is sufficient for you, don't go up to 1. See section 'Depth
        control' of
        https://wiki.jenkins-ci.org/display/JENKINS/Remote+access+API
        """
        assert isinstance(buildno, int)
        self.buildno = buildno
        self.job = job
        self.depth = depth
        JenkinsBase.__init__(self, url)

    def _poll(self, tree=None):
        # For build's we need more information for downstream and
        # upstream builds so we override the poll to get at the extra
        # data for build objects
        url = self.python_api_url(self.baseurl)
        return self.get_data(url, params={'depth': self.depth}, tree=tree)

    def __str__(self):
        return self._data['fullDisplayName']

    @property
    def name(self):
        return str(self)

    def get_description(self):
        return self._data["description"]

    def get_number(self):
        return self._data["number"]

    def get_status(self):
        return self._data["result"]

    def get_slave(self):
        return self._data["builtOn"]

    def get_revision(self):
        return getattr(self, '_get_%s_rev' % self._get_vcs(), lambda: None)()

    def get_revision_branch(self):
        return getattr(self, '_get_%s_rev_branch' % self._get_vcs(), lambda: None)()

    def get_repo_url(self):
        return getattr(self, '_get_%s_repo_url' % self._get_vcs(), lambda: None)()

    def get_params(self):
        """
        Return a dictionary of params names and their values or None
        if no parameters present
        """
        # This is what a parameter action looks like:
        # {'_class': 'hudson.model.ParametersAction', 'parameters': [
        #     {'_class': 'hudson.model.StringParameterValue',
        #      'value': '12',
        #      'name': 'FOO_BAR_BAZ'}]}
        actions = self._data.get('actions')
        if actions:
            parameters = {}
            for elem in actions:
                if elem.get('_class') == 'hudson.model.ParametersAction':
                    parameters = elem.get('parameters', {})
                    break
            return {pair['name']: pair.get('value') for pair in parameters}

        return {}

    def get_changeset_items(self):
        """
        Returns a list of changeSet items.

        Each item has structure as in following example:
        {
            "affectedPaths": [
                "content/rcm/v00-rcm-xccdf.xml"
            ],
            "author" : {
                "absoluteUrl": "http://jenkins_url/user/username79",
                "fullName": "username"
            },
            "commitId": "3097",
            "timestamp": 1414398423091,
            "date": "2014-10-27T08:27:03.091288Z",
            "msg": "commit message",
            "paths": [{
                "editType": "edit",
                "file": "/some/path/of/changed_file"
            }],
            "revision": 3097,
            "user": "username"
        }
        """
        if 'changeSet' in self._data:
            if 'items' in self._data['changeSet']:
                return self._data['changeSet']['items']
        elif 'changeSets' in self._data:
            if 'items' in self._data['changeSets']:
                return self._data['changeSets']['items']
        return []

    def _get_vcs(self):
        """
        Returns a string VCS.
        By default, 'git' will be used.
        """
        vcs = 'git'
        if 'changeSet' in self._data and 'kind' in self._data['changeSet']:
            vcs = self._data['changeSet']['kind'] or 'git'
        elif 'changeSets' in self._data and 'kind' in self._data['changeSets']:
            vcs = self._data['changeSets']['kind'] or 'git'
        return vcs

    def _get_svn_rev(self):
        warnings.warn(
            "This untested function may soon be removed from Jenkinsapi "
            "(get_svn_rev).")
        maxRevision = 0
        for repoPathSet in self._data["changeSet"]["revisions"]:
            maxRevision = max(repoPathSet["revision"], maxRevision)
        return maxRevision

    def _get_git_rev(self):
        # Sometimes we have None as part of actions. Filter those actions
        # which have lastBuiltRevision in them
        _actions = [x for x in self._data['actions']
                    if x and "lastBuiltRevision" in x]

        if _actions:
            return _actions[0]["lastBuiltRevision"]["SHA1"]

        return None

    def _get_hg_rev(self):
        warnings.warn(
            "This untested function may soon be removed from Jenkinsapi "
            "(_get_hg_rev).")
        return [x['mercurialNodeName']
                for x in self._data['actions'] if 'mercurialNodeName' in x][0]

    def _get_svn_rev_branch(self):
        raise NotImplementedError('_get_svn_rev_branch is not yet implemented')

    def _get_git_rev_branch(self):
        # Sometimes we have None as part of actions. Filter those actions
        # which have lastBuiltRevision in them
        _actions = [x for x in self._data['actions']
                    if x and "lastBuiltRevision" in x]

        return _actions[0]["lastBuiltRevision"]["branch"]

    def _get_hg_rev_branch(self):
        raise NotImplementedError('_get_hg_rev_branch is not yet implemented')

    def _get_git_repo_url(self):
        # Sometimes we have None as part of actions. Filter those actions
        # which have lastBuiltRevision in them
        _actions = [x for x in self._data['actions']
                    if x and "lastBuiltRevision" in x]
        # old Jenkins version have key remoteUrl v/s the new version has a list remoteUrls
        result = _actions[0].get("remoteUrls", _actions[0].get("remoteUrl"))
        if isinstance(result, list):
            result = ','.join(result)
        return result

    def _get_svn_repo_url(self):
        raise NotImplementedError('_get_svn_repo_url is not yet implemented')

    def _get_hg_repo_url(self):
        raise NotImplementedError('_get_hg_repo_url is not yet implemented')

    def get_duration(self):
        return datetime.timedelta(milliseconds=self._data["duration"])

    def get_build_url(self):
        return self._data['url']

    def get_artifacts(self):
        data = self.poll(tree='artifacts[relativePath,fileName]')
        for afinfo in data["artifacts"]:
            url = "%s/artifact/%s" % (self.baseurl,
                                      quote(afinfo["relativePath"]))
            af = Artifact(afinfo["fileName"], url, self,
                          relative_path=afinfo["relativePath"])
            yield af

    def get_artifact_dict(self):
        return dict(
            (af.relative_path, af) for af in self.get_artifacts()
        )

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
        warnings.warn(
            "This untested function may soon be removed from Jenkinsapi "
            "(get_master_job).")
        if self.get_master_job_name():
            return self.get_jenkins_obj().get_job(self.get_master_job_name())

        return None

    def get_master_build_number(self):
        """
        Get the master build number if it exist, None otherwise
        :return: int or None
        """
        warnings.warn(
            "This untested function may soon be removed from Jenkinsapi "
            "(get_master_build_number).")
        try:
            return int(self.get_actions()['parameters'][1]['value'])
        except KeyError:
            return None

    def get_master_build(self):
        """
        Get the master build if it exist, None otherwise
        :return Build or None
        """
        warnings.warn(
            "This untested function may soon be removed from Jenkinsapi "
            "(get_master_build).")
        master_job = self.get_master_job()
        if master_job:
            return master_job.get_build(self.get_master_build_number())

        return None

    def get_downstream_jobs(self):
        """
        Get the downstream jobs for this build
        :return List of jobs or None
        """
        warnings.warn(
            "This untested function may soon be removed from Jenkinsapi "
            "(get_downstream_jobs).")
        downstream_jobs = []
        try:
            for job_name in self.get_downstream_job_names():
                downstream_jobs.append(
                    self.get_jenkins_obj().get_job(job_name))
            return downstream_jobs
        except (IndexError, KeyError):
            return []

    def get_downstream_job_names(self):
        """
        Get the downstream job names for this build
        :return List of string or None
        """
        downstream_job_names = self.job.get_downstream_job_names()
        downstream_names = []
        try:
            fingerprints = self._data["fingerprint"]
            for fingerprint in fingerprints:
                for job_usage in fingerprint['usage']:
                    if job_usage['name'] in downstream_job_names:
                        downstream_names.append(job_usage['name'])
            return downstream_names
        except (IndexError, KeyError):
            return []

    def get_downstream_builds(self):
        """
        Get the downstream builds for this build
        :return List of Build or None
        """
        downstream_job_names = self.get_downstream_job_names()
        downstream_builds = []
        try:  # pylint: disable=R1702
            fingerprints = self._data["fingerprint"]
            for fingerprint in fingerprints:
                for job_usage in fingerprint['usage']:
                    if job_usage['name'] in downstream_job_names:
                        job = self.get_jenkins_obj().get_job(job_usage['name'])
                        for job_range in job_usage['ranges']['ranges']:
                            for build_id in range(job_range['start'],
                                                  job_range['end']):
                                downstream_builds.append(
                                    job.get_build(build_id))
            return downstream_builds
        except (IndexError, KeyError):
            return []

    def get_matrix_runs(self):
        """
        For a matrix job, get the individual builds for each
        matrix configuration
        :return: Generator of Build
        """
        if 'runs' in self._data:
            for rinfo in self._data['runs']:
                number = rinfo['number']
                if number == self._data['number']:
                    yield Build(rinfo['url'], number, self.job)

    def is_running(self):
        """
        Return a bool if running.
        """
        data = self.poll(tree='building')
        return data.get('building', False)

    def block(self):
        while self.is_running():
            time.sleep(1)

    def is_good(self):
        """
        Return a bool, true if the build was good.
        If the build is still running, return False.
        """
        return (not self.is_running()) and \
            self._data["result"] == STATUS_SUCCESS

    def block_until_complete(self, delay=15):
        assert isinstance(delay, int)
        count = 0
        while self.is_running():
            total_wait = delay * count
            log.info(
                msg="Waited %is for %s #%s to complete" %
                (total_wait, self.job.name, self.name))
            sleep(delay)
            count += 1

    def get_jenkins_obj(self):
        return self.job.get_jenkins_obj()

    def get_result_url(self):
        """
        Return the URL for the object which provides the job's result summary.
        """
        url_tpl = r"%stestReport/%s"
        return url_tpl % (self._data["url"], config.JENKINS_API)

    def get_resultset(self):
        """
        Obtain detailed results for this build.
        """
        result_url = self.get_result_url()
        if self.STR_TOTALCOUNT not in self.get_actions():
            raise NoResults(
                "%s does not have any published results" %
                str(self))
        buildstatus = self.get_status()
        if not self.get_actions()[self.STR_TOTALCOUNT]:
            raise NoResults(
                self.STR_TPL_NOTESTS_ERR %
                (str(self), buildstatus))
        obj_results = ResultSet(result_url, build=self)
        return obj_results

    def has_resultset(self):
        """
        Return a boolean, true if a result set is available. false if not.
        """
        return self.STR_TOTALCOUNT in self.get_actions()

    def get_actions(self):
        all_actions = {}
        for dct_action in self._data["actions"]:
            if dct_action is None:
                continue
            all_actions.update(dct_action)
        return all_actions

    def get_causes(self):
        """
        Returns a list of causes. There can be multiple causes lists and
        some of the can be empty. For instance, when a build is manually
        aborted, Jenkins could add an empty causes list to the actions
        dict. Empty ones are ignored.
        """
        all_causes = []
        for dct_action in self._data["actions"]:
            if dct_action is None:
                continue
            if 'causes' in dct_action and dct_action['causes']:
                all_causes.extend(dct_action['causes'])
        return all_causes

    def get_timestamp(self):
        """
        Returns build timestamp in UTC
        """
        # Java timestamps are given in miliseconds since the epoch start!
        naive_timestamp = datetime.datetime(
            *time.gmtime(self._data['timestamp'] / 1000.0)[:6])
        return pytz.utc.localize(naive_timestamp)

    def get_console(self):
        """
        Return the current state of the text console.
        """
        url = "%s/consoleText" % self.baseurl
        content = self.job.jenkins.requester.get_url(url).content
        # This check was made for Python 3.x
        # In this version content is a bytes string
        # By contract this function must return string
        if isinstance(content, str):
            return content
        elif isinstance(content, bytes):
            return content.decode('ISO-8859-1')
        else:
            raise JenkinsAPIException('Unknown content type for console')

    def stream_logs(self, interval=0):
        """
        Return generator which streams parts of text console.
        """
        url = "%s/logText/progressiveText" % self.baseurl
        size = 0
        more_data = True
        while more_data:
            resp = self.job.jenkins.requester.get_url(url, params={'start': size})
            content = resp.content
            if content:
                if isinstance(content, str):
                    yield content
                elif isinstance(content, bytes):
                    yield content.decode('ISO-8859-1')
                else:
                    raise JenkinsAPIException('Unknown content type for console')
            size = resp.headers['X-Text-Size']
            more_data = resp.headers.get('X-More-Data')
            sleep(interval)

    def get_estimated_duration(self):
        """
        Return the estimated build duration (in seconds) or none.
        """
        try:
            eta_ms = self._data["estimatedDuration"]
            return max(0, eta_ms / 1000.0)
        except KeyError:
            return None

    def stop(self):
        """
        Stops the build execution if it's running
        :return boolean True if succeded False otherwise or the build
            is not running
        """
        if self.is_running():
            url = "%s/stop" % self.baseurl
            # Starting from Jenkins 2.7 stop function sometimes breaks
            # on redirect to job page. Call to stop works fine, and
            # we don't need to have job page here.
            self.job.jenkins.requester.post_and_confirm_status(
                url, data='', valid=[302, 200, 500, ])
            return True
        return False

    def get_env_vars(self):
        """
        Return the environment variables.

        This method is using the Environment Injector plugin:
        https://wiki.jenkins-ci.org/display/JENKINS/EnvInject+Plugin
        """
        url = self.python_api_url('%s/injectedEnvVars' % self.baseurl)
        try:
            data = self.get_data(url, params={'depth': self.depth})
        except HTTPError as ex:
            warnings.warn('Make sure the Environment Injector plugin '
                          'is installed.')
            raise ex
        return data['envMap']

    def toggle_keep(self):
        """
        Toggle "keep this build forever" on and off
        """
        url = '%s/toggleLogKeep' % self.baseurl
        self.get_jenkins_obj().requester.post_and_confirm_status(url, data={})
        self._data = self._poll()

    def is_kept_forever(self):
        return self._data["keepLog"]
