import mock
import unittest

import requests
from jenkinsapi.jenkins import Requester
from jenkinsapi.custom_exceptions import JenkinsAPIException


class TestQueue(unittest.TestCase):

    def test_get_request_dict_auth(self):
        req = Requester('foo', 'bar')

        req_return = req.get_request_dict(
            params={},
            data=None,
            headers=None
        )
        self.assertTrue(isinstance(req_return, dict))
        self.assertTrue(req_return.get('auth'))
        self.assertTrue(req_return['auth'] == ('foo', 'bar'))

    def test_get_request_dict_wrong_params(self):
        req = Requester('foo', 'bar')

        with self.assertRaises(AssertionError) as na:
            req.get_request_dict(
                params='wrong',
                data=None,
                headers=None
            )
        self.assertTrue(na.exception.message == "Params must be a dict, got 'wrong'")

    def test_get_request_dict_correct_params(self):
        req = Requester('foo', 'bar')

        req_return = req.get_request_dict(
            params={'param': 'value'},
            data=None,
            headers=None
        )

        self.assertTrue(isinstance(req_return, dict))
        self.assertTrue(req_return.get('params'))
        self.assertTrue(req_return['params'] == {'param': 'value'})

    def test_get_request_dict_wrong_headers(self):
        req = Requester('foo', 'bar')

        with self.assertRaises(AssertionError) as na:
            req.get_request_dict(
                params={},
                data=None,
                headers='wrong'
            )
        self.assertTrue(na.exception.message == "headers must be a dict, got 'wrong'")

    def test_get_request_dict_correct_headers(self):
        req = Requester('foo', 'bar')

        req_return = req.get_request_dict(
            params={'param': 'value'},
            data=None,
            headers={'header': 'value'}
        )

        self.assertTrue(isinstance(req_return, dict))
        self.assertTrue(req_return.get('headers'))
        self.assertTrue(req_return['headers'] == {'header': 'value'})

    def test_get_request_dict_data_passed(self):
        req = Requester('foo', 'bar')

        req_return = req.get_request_dict(
            params={'param': 'value'},
            data='some data',
            headers={'header': 'value'}
        )

        self.assertTrue(isinstance(req_return, dict))
        print req_return.get('data')
        self.assertTrue(req_return.get('data'))
        self.assertTrue(req_return['data'] == 'some data')

    def test_get_request_dict_data_not_passed(self):
        req = Requester('foo', 'bar')

        req_return = req.get_request_dict(
            params={'param': 'value'},
            data=None,
            headers={'header': 'value'}
        )

        self.assertTrue(isinstance(req_return, dict))
        self.assertFalse(req_return.get('data'))

    @mock.patch.object(requests, 'get')
    def test_get_url_get(self, _get):
        _get.return_value = 'SUCCESS'
        req = Requester('foo', 'bar')
        response = req.get_url(
            'http://dummy',
            params={'param': 'value'},
            headers=None)
        self.assertTrue(response == 'SUCCESS')

    @mock.patch.object(requests, 'post')
    def test_get_url_post(self, _post):
        _post.return_value = 'SUCCESS'
        req = Requester('foo', 'bar')
        response = req.post_url(
            'http://dummy',
            params={'param': 'value'},
            headers=None)
        self.assertTrue(response == 'SUCCESS')

    @mock.patch.object(requests, 'post')
    def test_post_xml_and_confirm_status_empty_xml(self, _post):
        _post.return_value = 'SUCCESS'
        req = Requester('foo', 'bar')
        with self.assertRaises(AssertionError) as ae:
            req.post_xml_and_confirm_status(
                url='http://dummy',
                params={'param': 'value'},
                data=None
            )

        self.assertTrue(ae.exception.message == "Unexpected type of parameter 'data': <type 'NoneType'>. Expected (str, dict)")

    @mock.patch.object(requests, 'post')
    def test_post_xml_and_confirm_status_some_xml(self, _post):
        response = requests.Response()
        response.status_code = 200
        _post.return_value = response
        req = Requester('foo', 'bar')
        ret = req.post_xml_and_confirm_status(
            url='http://dummy',
            params={'param': 'value'},
            data='<xml/>'
        )
        self.assertTrue(isinstance(ret, requests.Response))

    @mock.patch.object(requests, 'post')
    def test_post_and_confirm_status_empty_data(self, _post):
        _post.return_value = 'SUCCESS'
        req = Requester('foo', 'bar')
        with self.assertRaises(AssertionError) as ae:
            req.post_and_confirm_status(
                url='http://dummy',
                params={'param': 'value'},
                data=None
            )

        self.assertTrue(ae.exception.message == "Unexpected type of parameter 'data': <type 'NoneType'>. Expected (str, dict)")

    @mock.patch.object(requests, 'post')
    def test_post_and_confirm_status_some_data(self, _post):
        response = requests.Response()
        response.status_code = 200
        _post.return_value = response
        req = Requester('foo', 'bar')
        ret = req.post_and_confirm_status(
            url='http://dummy',
            params={'param': 'value'},
            data='some data'
        )
        self.assertTrue(isinstance(ret, requests.Response))

    @mock.patch.object(requests, 'post')
    def test_post_and_confirm_status_bad_result(self, _post):
        response = requests.Response()
        response.status_code = 500
        _post.return_value = response

        req = Requester('foo', 'bar')
        with self.assertRaises(JenkinsAPIException) as ae:
            req.post_and_confirm_status(
                url='http://dummy',
                params={'param': 'value'},
                data='some data'
            )

        print ae.exception.message
        self.assertTrue(ae.exception.message == "Operation failed. url=None, data=some data, headers={'Content-Type': 'application/x-www-form-urlencoded'}, status=500, text=")

    @mock.patch.object(requests, 'get')
    def test_get_and_confirm_status(self, _get):
        response = requests.Response()
        response.status_code = 200
        _get.return_value = response
        req = Requester('foo', 'bar')
        ret = req.get_and_confirm_status(
            url='http://dummy',
            params={'param': 'value'}
        )
        self.assertTrue(isinstance(ret, requests.Response))

    @mock.patch.object(requests, 'get')
    def test_get_and_confirm_status_bad_result(self, _get):
        response = requests.Response()
        response.status_code = 500
        _get.return_value = response

        req = Requester('foo', 'bar')
        with self.assertRaises(JenkinsAPIException) as ae:
            req.get_and_confirm_status(
                url='http://dummy',
                params={'param': 'value'}
            )

        print ae.exception.message
        self.assertTrue(ae.exception.message == "Operation failed. url=None, headers=None, status=500, text=")
