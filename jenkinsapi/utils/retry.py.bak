import logging
import time
import urllib2

log = logging.getLogger( __name__ )

IGNORE_EXCEPTIONS = [ AttributeError, KeyboardInterrupt ]

DEFAULT_SLEEP_TIME = 1

def retry_function( tries, fn, *args, **kwargs ):
    """
    Retry function - calls an unreliable function n times before giving up, if tries is exceeded
    and it still fails the most recent exception is raised.
    """
    assert isinstance( tries, int ), "Tries should be a non-zero positive integer"
    assert tries > 0, "Tries should be a non-zero positive integer"
    for attempt in range(0, tries):
        attemptno = attempt + 1
        if attemptno == tries:
            log.warn( "Last chance: #%i of %i" % ( attemptno, tries ) )
        elif tries > attempt > 0:
            log.warn( "Attempt #%i of %i" % ( attemptno, tries ) )
        try:
            result = fn( *args, **kwargs )
            if attempt > 0:
                log.info( "Result obtained after attempt %i" % attemptno )
            return result
        except urllib2.HTTPError, e:
            if e.code == 404:
                raise
            log.exception(e)
        except Exception, e:
            if type(e) in IGNORE_EXCEPTIONS:
                # Immediatly raise in some cases.
                raise
        try:
            fn_name = fn.__name__
        except AttributeError:
            fn_name = "Anonymous Function"
        log.exception(e)
        if attemptno == tries:
            log.error( "%s failed at attempt %i, give up." % ( fn_name , attemptno ) )
            raise
        log.warn( "%s failed at attempt %i, trying again." % ( fn_name , attemptno ) )
        time.sleep( DEFAULT_SLEEP_TIME )
