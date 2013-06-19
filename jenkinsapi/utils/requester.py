import requests
from jenkinsapi.exceptions import JenkinsAPIException


class Requester(object):

    """
    A class which carries out HTTP requests. You can replace this class with one of your own implementation if you require
    some other way to access Jenkins.

    This default class can handle simple authentication only.
    """

    STATUS_OK = 200

    def __init__(self, username=None, password=None):
        if username:
            assert password, 'Cannot set a username without a password!'

        self.username = username
        self.password = password

    def get_request_dict(self, url, params, data, headers):
        requestKwargs = {}
        if self.username:
            requestKwargs['auth'] = (self.username, self.password)

        if params:
            assert isinstance(
                params, dict), 'Params must be a dict, got %s' % repr(params)
            requestKwargs['params'] = params

        if headers:
            assert isinstance(
                headers, dict), 'headers must be a dict, got %s' % repr(headers)
            requestKwargs['headers'] = headers

        if not data == None:
            # It may seem odd, but some Jenkins operations require posting
            # an empty string.
            requestKwargs['data'] = data
        return requestKwargs

    def get_url(self, url, params=None, headers=None):
        requestKwargs = self.get_request_dict(url, params, None, headers)
        return requests.get(url, **requestKwargs)


    def post_url(self, url, params=None, data=None, headers=None):
        requestKwargs = self.get_request_dict(url, params, data, headers)
        return requests.post(url, **requestKwargs)

    def post_xml_and_confirm_status(self, url, params=None, data=None):
        headers = {'Content-Type': 'text/xml'}
        return self.post_and_confirm_status(url, params, data, headers)

    def post_and_confirm_status(self, url, params=None, data=None, headers=None):
        assert isinstance(data, (
            str, dict)), "Unexpected data type: %s" % repr(data)

        if not headers:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = self.post_url(url, params, data, headers)
        if not response.status_code == self.STATUS_OK:
            raise JenkinsAPIException('Operation failed. url={0}, data={1}, headers={2}, status={3}, text={4}'.format(
                response.url, data, headers, response.status_code, response.text.encode('UTF-8')))
        return response

    def get_and_confirm_status(self, url, params=None, headers=None):
        response = self.get_url(url, params, headers)
        if not response.status_code == self.STATUS_OK:
            raise JenkinsAPIException('Operation failed. url={0}, headers={1}, status={2}, text={3}'.format(
                response.url, headers, response.status_code, response.text.encode('UTF-8')))
        return response
