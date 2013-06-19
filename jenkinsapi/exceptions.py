class JenkinsAPIException(Exception):
    """
    Base class for all errors
    """

class ArtifactsMissing(JenkinsAPIException):
    """
    Cannot find a build with all of the required artifacts.
    """

class UnknownJob( KeyError, JenkinsAPIException):
    """
    Jenkins does not recognize the job requested.
    """

class UnknownView( KeyError, JenkinsAPIException):
    """
    Jenkins does not recognize the view requested.
    """

class UnknownNode( KeyError, JenkinsAPIException):
    """
    Jenkins does not recognize the node requested.
    """

class UnknownQueueItem( KeyError, JenkinsAPIException):
    """
    Jenkins does not recognize the requested queue item
    """

class ArtifactBroken(JenkinsAPIException):
    """
    An artifact is broken, wrong
    """

class TimeOut( JenkinsAPIException ):
    """
    Some jobs have taken too long to complete.
    """

class WillNotBuild(JenkinsAPIException):
    """
    Cannot trigger a new build.
    """

class NoBuildData(JenkinsAPIException):
    """
    A job has no build data.
    """

class NoResults(JenkinsAPIException):
    """
    A build did not publish any results.
    """

class FailedNoResults(NoResults):
    """
    A build did not publish any results because it failed
    """

class BadURL(ValueError,JenkinsAPIException):
    """
    A URL appears to be broken
    """

class NotFound(JenkinsAPIException):
    """
    Resource cannot be found
    """

class NotAuthorized(JenkinsAPIException):
    """Not Authorized to access resource"""
    # Usually thrown when we get a 403 returned

class NotSupportSCM(JenkinsAPIException):
    """
    It's a SCM that does not supported by current version of jenkinsapi
    """

class NotConfiguredSCM(JenkinsAPIException):
    """
    It's a job that doesn't have configured SCM
    """
class NotInQueue(JenkinsAPIException):
    """
    It's a job that is not in the queue
    """
