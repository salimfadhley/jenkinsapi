"""
Module for jenkinsapi requester (which is a wrapper around python-requests)
"""
import requests

try:
    import urlparse
except ImportError:
    # Python3
    import urllib.parse as urlparse

from jenkinsapi.custom_exceptions import JenkinsAPIException, PostRequired
# import logging

# these two lines enable debugging at httplib level
# (requests->urllib3->httplib)
# you will see the REQUEST, including HEADERS and DATA, and RESPONSE
# with HEADERS but without DATA.
# the only thing missing will be the response.body which is not logged.
# import httplib
# httplib.HTTPConnection.debuglevel = 1

# you need to initialize logging, otherwise you will not see anything
# from requests
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True


class Requester(object):

    """
    A class which carries out HTTP requests. You can replace this
    class with one of your own implementation if you require some other
    way to access Jenkins.

    This default class can handle simple authentication only.
    """

    VALID_STATUS_CODES = [200, ]

    def __init__(
            self, username=None, password=None, ssl_verify=True, baseurl=None):
        if username:
            assert password, 'Cannot set a username without a password!'

        self.base_scheme = urlparse.urlsplit(
            baseurl).scheme if baseurl else None
        self.username = username
        self.password = password
        self.ssl_verify = ssl_verify

    def get_request_dict(
            self, params=None, data=None, files=None, headers=None, **kwargs):
        requestKwargs = kwargs
        if self.username:
            requestKwargs['auth'] = (self.username, self.password)

        if params:
            assert isinstance(
                params, dict), 'Params must be a dict, got %s' % repr(params)
            requestKwargs['params'] = params

        if headers:
            assert isinstance(
                headers, dict), \
                'headers must be a dict, got %s' % repr(headers)
            requestKwargs['headers'] = headers

        requestKwargs['verify'] = self.ssl_verify

        if data:
            # It may seem odd, but some Jenkins operations require posting
            # an empty string.
            requestKwargs['data'] = data

        if files:
            requestKwargs['files'] = files

        return requestKwargs

    def _update_url_scheme(self, url):
        """
        Updates scheme of given url to the one used in Jenkins baseurl.
        """
        if self.base_scheme and not url.startswith("%s://" % self.base_scheme):
            url_split = urlparse.urlsplit(url)
            url = urlparse.urlunsplit(
                [
                    self.base_scheme,
                    url_split.netloc,
                    url_split.path,
                    url_split.query,
                    url_split.fragment
                ]
            )
        return url

    def get_url(self, url, params=None, headers=None, allow_redirects=True,
                stream=False):
        requestKwargs = self.get_request_dict(
            params=params,
            headers=headers,
            allow_redirects=allow_redirects,
            stream=stream
        )
        return requests.get(self._update_url_scheme(url), **requestKwargs)

    def post_url(self, url, params=None, data=None, files=None,
                 headers=None, allow_redirects=True):
        requestKwargs = self.get_request_dict(
            params=params,
            data=data,
            files=files,
            headers=headers,
            allow_redirects=allow_redirects)
        return requests.post(self._update_url_scheme(url), **requestKwargs)

    def post_xml_and_confirm_status(
            self, url, params=None, data=None, valid=None):
        headers = {'Content-Type': 'text/xml'}
        return self.post_and_confirm_status(
            url, params=params, data=data, headers=headers, valid=valid)

    def post_and_confirm_status(
            self, url, params=None, data=None, files=None, headers=None,
            valid=None, allow_redirects=True):
        valid = valid or self.VALID_STATUS_CODES
        if not headers and not files:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        assert data is not None, "Post messages must have data"

        response = self.post_url(
            url,
            params,
            data,
            files,
            headers,
            allow_redirects)
        if response.status_code not in valid:
            raise JenkinsAPIException(
                'Operation failed. url={0}, data={1}, headers={2}, '
                'status={3}, text={4}'.format(
                    response.url, data, headers, response.status_code,
                    response.text.encode('UTF-8')
                )
            )
        return response

    def get_and_confirm_status(
            self, url, params=None, headers=None, valid=None, stream=False):
        valid = valid or self.VALID_STATUS_CODES
        response = self.get_url(url, params, headers, stream=stream)
        if response.status_code not in valid:
            if response.status_code == 405:         # POST required
                raise PostRequired('POST required for url {0}'.format(url))
            else:
                raise JenkinsAPIException(
                    'Operation failed. url={0}, headers={1}, status={2}, '
                    'text={3}'.format(
                        response.url, headers, response.status_code,
                        response.text.encode('UTF-8')
                    )
                )
        return response
