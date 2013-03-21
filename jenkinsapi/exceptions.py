class ArtifactsMissing(Exception):
    """
    Cannot find a build with all of the required artifacts.
    """

class UnknownJob( KeyError ):
    """
    Jenkins does not recognize the job requested.
    """

class ArtifactBroken(Exception):
    """
    An artifact is broken, wrong
    """

class TimeOut( Exception ):
    """
    Some jobs have taken too long to complete.
    """

class WillNotBuild(Exception):
    """
    Cannot trigger a new build.
    """

class NoBuildData(Exception):
    """
    A job has no build data.
    """

class NoResults(Exception):
    """
    A build did not publish any results.
    """

class FailedNoResults(NoResults):
    """
    A build did not publish any results because it failed
    """

class BadURL(ValueError):
    """
    A URL appears to be broken
    """

class NotFound(Exception):
    """
    Resource cannot be found
    """

class NotAuthorized(Exception):
    """Not Authorized to access resource"""
    # Usually thrown when we get a 403 returned

class NotSupportSCM(Exception):
    """
    It's a SCM that does not supported by current version of jenkinsapi
    """

class NotConfiguredSCM(Exception):
    """
    It's a job that doesn't have configured SCM
    """
class NotInQueue(Exception):
    """
    It's a job that is not in the queue
    """
