"""
This module is a collection of helpful, high-level functions
for automating common tasks.
Many of these functions were designed to be exposed to the command-line,
hence they have simple string arguments.
"""
import os
import time
import logging

try:
    from urllib import parse as urlparse
except ImportError:
    # Python3
    from urllib2 import urlparse

from jenkinsapi import constants
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.artifact import Artifact
from jenkinsapi.custom_exceptions import ArtifactsMissing, TimeOut, BadURL

log = logging.getLogger(__name__)


def get_latest_test_results(jenkinsurl, jobname, username=None, password=None,
                            ssl_verify=True):
    """
    A convenience function to fetch down the very latest test results
    from a jenkins job.
    """
    latestbuild = get_latest_build(jenkinsurl, jobname, username=username,
                                   password=password, ssl_verify=ssl_verify)
    res = latestbuild.get_resultset()
    return res


def get_latest_build(jenkinsurl, jobname, username=None, password=None,
                     ssl_verify=True):
    """
    A convenience function to fetch down the very latest test results
    from a jenkins job.
    """
    jenkinsci = Jenkins(jenkinsurl, username=username, password=password,
                        ssl_verify=ssl_verify)
    job = jenkinsci[jobname]
    return job.get_last_build()


def get_latest_complete_build(jenkinsurl, jobname,
                              username=None, password=None, ssl_verify=True):
    """
    A convenience function to fetch down the very latest test results
    from a jenkins job.
    """
    jenkinsci = Jenkins(jenkinsurl, username=username, password=password,
                        ssl_verify=ssl_verify)
    job = jenkinsci[jobname]
    return job.get_last_completed_build()


def get_build(jenkinsurl, jobname, build_no, username=None, password=None,
              ssl_verify=True):
    """
    A convenience function to fetch down the test results
    from a jenkins job by build number.
    """
    jenkinsci = Jenkins(jenkinsurl, username=username, password=password,
                        ssl_verify=ssl_verify)
    job = jenkinsci[jobname]
    return job.get_build(build_no)


def get_artifacts(jenkinsurl, jobid=None, build_no=None,
                  username=None, password=None, ssl_verify=True):
    """
    Find all the artifacts for the latest build of a job.
    """
    jenkinsci = Jenkins(jenkinsurl, username=username, password=password,
                        ssl_verify=ssl_verify)
    job = jenkinsci[jobid]
    if build_no:
        build = job.get_build(build_no)
    else:
        build = job.get_last_good_build()
    artifacts = build.get_artifact_dict()
    log.info(msg="Found %i artifacts in '%s'"
             % (len(artifacts.keys()), build_no))
    return artifacts


def search_artifacts(jenkinsurl, jobid, artifact_ids=None,
                     username=None, password=None, ssl_verify=True):
    """
    Search the entire history of a jenkins job for a list of artifact names.
    If same_build is true then ensure that all artifacts come from the
    same build of the job
    """
    if len(artifact_ids) == 0 or artifact_ids is None:
        return []

    jenkinsci = Jenkins(jenkinsurl, username=username, password=password,
                        ssl_verify=ssl_verify)
    job = jenkinsci[jobid]
    build_ids = job.get_build_ids()
    for build_id in build_ids:
        build = job.get_build(build_id)
        artifacts = build.get_artifact_dict()
        if set(artifact_ids).issubset(set(artifacts.keys())):
            return dict((a, artifacts[a]) for a in artifact_ids)
        missing_artifacts = set(artifact_ids) - set(artifacts.keys())
        log.debug(msg="Artifacts %s missing from %s #%i"
                  % (", ".join(missing_artifacts), jobid, build_id))
    # noinspection PyUnboundLocalVariable
    raise ArtifactsMissing(missing_artifacts)


def grab_artifact(jenkinsurl, jobid, artifactid, targetdir,
                  username=None, password=None,
                  strict_validation=False, ssl_verify=True):
    """
    Convenience method to find the latest good version of an artifact and
    save it to a target directory.
    Directory is made automatically if not exists.
    """
    artifacts = get_artifacts(jenkinsurl, jobid,
                              username=username, password=password,
                              ssl_verify=ssl_verify)
    artifact = artifacts[artifactid]
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)
    artifact.save_to_dir(targetdir, strict_validation)


def block_until_complete(jenkinsurl, jobs, maxwait=12000, interval=30,
                         raise_on_timeout=True, username=None, password=None,
                         ssl_verify=True):
    """
    Wait until all of the jobs in the list are complete.
    """
    assert maxwait > 0
    assert maxwait > interval
    assert interval > 0

    obj_jenkins = Jenkins(jenkinsurl, username=username, password=password,
                          ssl_verify=ssl_verify)
    obj_jobs = [obj_jenkins[jid] for jid in jobs]
    for time_left in range(maxwait, 0, -interval):
        still_running = [j for j in obj_jobs if j.is_queued_or_running()]
        if not still_running:
            return
        str_still_running = ", ".join('"%s"' % str(a) for a in still_running)
        log.warning(
            "Waiting for jobs %s to complete. Will wait another %is",
            str_still_running, time_left)
        time.sleep(interval)
    if raise_on_timeout:
        # noinspection PyUnboundLocalVariable
        raise TimeOut("Waited too long for these jobs to complete: %s"
                      % str_still_running)


def get_view_from_url(url, username=None, password=None, ssl_verify=True):
    """
    Factory method
    """
    matched = constants.RE_SPLIT_VIEW_URL.search(url)
    if not matched:
        raise BadURL("Cannot parse URL %s" % url)
    jenkinsurl, view_name = matched.groups()
    jenkinsci = Jenkins(jenkinsurl, username=username, password=password,
                        ssl_verify=ssl_verify)
    return jenkinsci.views[view_name]


def get_nested_view_from_url(url, username=None, password=None,
                             ssl_verify=True):
    """
    Returns View based on provided URL. Convenient for nested views.
    """
    matched = constants.RE_SPLIT_VIEW_URL.search(url)
    if not matched:
        raise BadURL("Cannot parse URL %s" % url)
    jenkinsci = Jenkins(matched.group(0), username=username, password=password,
                        ssl_verify=ssl_verify)
    return jenkinsci.get_view_by_url(url)


def install_artifacts(artifacts, dirstruct, installdir, basestaticurl,
                      strict_validation=False):
    """
    Install the artifacts.
    """
    assert basestaticurl.endswith("/"), "Basestaticurl should end with /"
    installed = []
    for reldir, artifactnames in dirstruct.items():
        destdir = os.path.join(installdir, reldir)
        if not os.path.exists(destdir):
            log.warning("Making install directory %s", destdir)
            os.makedirs(destdir)
        else:
            assert os.path.isdir(destdir)
        for artifactname in artifactnames:
            destpath = os.path.abspath(os.path.join(destdir, artifactname))
            if artifactname in artifacts.keys():
                # The artifact must be loaded from jenkins
                theartifact = artifacts[artifactname]
            else:
                # It's probably a static file,
                # we can get it from the static collection
                staticurl = urlparse.urljoin(basestaticurl, artifactname)
                theartifact = Artifact(artifactname, staticurl, None)
            theartifact.save(destpath, strict_validation)
            installed.append(destpath)
    return installed


def search_artifact_by_regexp(jenkinsurl, jobid, artifactRegExp,
                              username=None, password=None, ssl_verify=True):
    '''
    Search the entire history of a hudson job for a build which has an
    artifact whose name matches a supplied regular expression.
    Return only that artifact.

    @param jenkinsurl: The base URL of the jenkins server
    @param jobid: The name of the job we are to search through
    @param artifactRegExp: A compiled regular expression object
        (not a re-string)
    @param username: Jenkins login user name, optional
    @param password: Jenkins login password, optional
    '''
    job = Jenkins(jenkinsurl, username=username, password=password,
                  ssl_verify=ssl_verify)
    j = job[jobid]

    build_ids = j.get_build_ids()

    for build_id in build_ids:
        build = j.get_build(build_id)

        artifacts = build.get_artifact_dict()

        try:
            it = artifacts.iteritems()
        except AttributeError:
            # Python3
            it = artifacts.items()

        for name, art in it:
            md_match = artifactRegExp.search(name)

            if md_match:
                return art

    raise ArtifactsMissing()
