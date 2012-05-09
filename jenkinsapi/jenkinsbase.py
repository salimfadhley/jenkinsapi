import urllib2
import logging
import pprint
from jenkinsapi import config
from jenkinsapi.utils.retry import retry_function

log = logging.getLogger(__name__)

class JenkinsBase(object):
    """
    This appears to be the base object that all other jenkins objects are inherited from
    """
    RETRY_ATTEMPTS = 5

    def __repr__(self):
        return """<%s.%s %s>""" % (self.__class__.__module__,
                                   self.__class__.__name__,
                                   str( self ))

    def print_data(self):
        pprint.pprint(self._data)

    def __str__(self):
        raise NotImplemented

    def __init__(self, baseurl, poll=True):
        """
        Initialize a jenkins connection
        """
        self.baseurl = baseurl
        if poll:
            try:
                self.poll()
            except urllib2.HTTPError, hte:
                log.exception(hte)
                log.warn( "Failed to conenct to %s" % baseurl )
                raise

    def poll(self):
        self._data = self._poll()

    def _poll(self):
        url = self.python_api_url(self.baseurl)
        return retry_function(self.RETRY_ATTEMPTS , self.get_data, url)

    def get_jenkins_obj(self):
        """Not implemented, abstract method implemented by child classes"""
        raise NotImplemented("Abstract method, implemented by child classes")

    @classmethod
    def python_api_url(cls, url):
        if url.endswith(config.JENKINS_API):
            return url
        else:
            if url.endswith(r"/"):
                fmt="%s%s"
            else:
                fmt = "%s/%s"
            return fmt % (url, config.JENKINS_API)

    def get_data(self, url):
        """
        Find out how to connect, and then grab the data.
        """
        fn_urlopen = self.get_jenkins_obj().get_opener()
        try:
            stream = fn_urlopen(url)
            result = eval(stream.read())
        except urllib2.HTTPError, e:
            log.warn("Error reading %s" % url)
            log.exception(e)
            raise
        return result

    def post_data(self, url, content):
        request = urllib2.Request(url, content)
        result = urllib2.urlopen(request).read().strip()
        return result

    def hit_url(self, url ):
        fn_urlopen = self.get_jenkins_obj().get_opener()
        try:
            stream = fn_urlopen( url )
            html_result = stream.read()
        except urllib2.HTTPError, e:
            log.debug( "Error reading %s" % url )
            log.exception(e)
            raise
        return html_result