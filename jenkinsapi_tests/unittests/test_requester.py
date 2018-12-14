from __future__ import print_function
import pytest
import requests
from jenkinsapi.jenkins import Requester
from jenkinsapi.custom_exceptions import JenkinsAPIException


def test_get_request_dict_auth():
    req = Requester('foo', 'bar')

    req_return = req.get_request_dict(
        params={},
        data=None,
        headers=None
    )
    assert isinstance(req_return, dict)
    assert req_return.get('auth')
    assert req_return['auth'] == ('foo', 'bar')


def test_get_request_dict_wrong_params():
    req = Requester('foo', 'bar')

    with pytest.raises(AssertionError) as na:
        req.get_request_dict(
            params='wrong',
            data=None,
            headers=None
        )
    assert "Params must be a dict, got 'wrong'" in str(na.value)


def test_get_request_dict_correct_params():
    req = Requester('foo', 'bar')

    req_return = req.get_request_dict(
        params={'param': 'value'},
        data=None,
        headers=None
    )

    assert isinstance(req_return, dict)
    assert req_return.get('params')
    assert req_return['params'] == {'param': 'value'}


def test_get_request_dict_wrong_headers():
    req = Requester('foo', 'bar')

    with pytest.raises(AssertionError) as na:
        req.get_request_dict(
            params={},
            data=None,
            headers='wrong'
        )
    assert "headers must be a dict, got 'wrong'" in str(na.value)


def test_get_request_dict_correct_headers():
    req = Requester('foo', 'bar')

    req_return = req.get_request_dict(
        params={'param': 'value'},
        data=None,
        headers={'header': 'value'}
    )

    assert isinstance(req_return, dict)
    assert req_return.get('headers')
    assert req_return['headers'] == {'header': 'value'}


def test_get_request_dict_data_passed():
    req = Requester('foo', 'bar')

    req_return = req.get_request_dict(
        params={'param': 'value'},
        data='some data',
        headers={'header': 'value'}
    )

    assert isinstance(req_return, dict)
    assert req_return.get('data')
    assert req_return['data'] == 'some data'


def test_get_request_dict_data_not_passed():
    req = Requester('foo', 'bar')

    req_return = req.get_request_dict(
        params={'param': 'value'},
        data=None,
        headers={'header': 'value'}
    )

    assert isinstance(req_return, dict)
    assert req_return.get('data') is None


def test_get_url_get(monkeypatch):
    def fake_get(*args, **kwargs):  # pylint: disable=unused-argument
        return 'SUCCESS'

    monkeypatch.setattr(requests, 'get', fake_get)

    req = Requester('foo', 'bar')
    response = req.get_url(
        'http://dummy',
        params={'param': 'value'},
        headers=None)

    assert response == 'SUCCESS'


def test_get_url_post(monkeypatch):
    def fake_post(*args, **kwargs):  # pylint: disable=unused-argument
        return 'SUCCESS'

    monkeypatch.setattr(requests, 'post', fake_post)

    req = Requester('foo', 'bar')
    response = req.post_url(
        'http://dummy',
        params={'param': 'value'},
        headers=None)

    assert response == 'SUCCESS'


def test_post_xml_empty_xml(monkeypatch):
    def fake_post(*args, **kwargs):  # pylint: disable=unused-argument
        return 'SUCCESS'

    monkeypatch.setattr(requests, 'post', fake_post)

    req = Requester('foo', 'bar')
    with pytest.raises(AssertionError):
        req.post_xml_and_confirm_status(
            url='http://dummy',
            params={'param': 'value'},
            data=None
        )


def test_post_xml_and_confirm_status_some_xml(monkeypatch):
    class FakeResponse(requests.Response):
        def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
            self.status_code = 200

    def fake_post(*args, **kwargs):  # pylint: disable=unused-argument
        return FakeResponse()

    monkeypatch.setattr(requests, 'post', fake_post)

    req = Requester('foo', 'bar')
    ret = req.post_xml_and_confirm_status(
        url='http://dummy',
        params={'param': 'value'},
        data='<xml/>'
    )
    assert isinstance(ret, requests.Response)


def test_post_and_confirm_status_empty_data(monkeypatch):
    def fake_post(*args, **kwargs):  # pylint: disable=unused-argument
        return 'SUCCESS'

    monkeypatch.setattr(requests, 'post', fake_post)

    req = Requester('foo', 'bar')
    with pytest.raises(AssertionError):
        req.post_and_confirm_status(
            url='http://dummy',
            params={'param': 'value'},
            data=None
        )


def test_post_and_confirm_status_some_data(monkeypatch):
    class FakeResponse(requests.Response):
        def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
            self.status_code = 200

    def fake_post(*args, **kwargs):  # pylint: disable=unused-argument
        return FakeResponse()

    monkeypatch.setattr(requests, 'post', fake_post)

    req = Requester('foo', 'bar')
    ret = req.post_and_confirm_status(
        url='http://dummy',
        params={'param': 'value'},
        data='some data'
    )
    assert isinstance(ret, requests.Response)


def test_post_and_confirm_status_bad_result(monkeypatch):
    class FakeResponse(object):
        def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
            self.status_code = 500
            self.url = 'http://dummy'
            self.text = 'something'

    def fake_post(*args, **kwargs):  # pylint: disable=unused-argument
        return FakeResponse()

    monkeypatch.setattr(requests, 'post', fake_post)

    req = Requester('foo', 'bar')
    with pytest.raises(JenkinsAPIException):
        req.post_and_confirm_status(
            url='http://dummy',
            params={'param': 'value'},
            data='some data'
        )


def test_get_and_confirm_status(monkeypatch):
    class FakeResponse(requests.Response):
        def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
            self.status_code = 200

    def fake_get(*args, **kwargs):  # pylint: disable=unused-argument
        return FakeResponse()

    monkeypatch.setattr(requests, 'get', fake_get)

    req = Requester('foo', 'bar')
    ret = req.get_and_confirm_status(
        url='http://dummy',
        params={'param': 'value'}
    )
    assert isinstance(ret, requests.Response)


def test_get_and_confirm_status_bad_result(monkeypatch):
    class FakeResponse(object):
        def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
            self.status_code = 500
            self.url = 'http://dummy'
            self.text = 'something'

    def fake_get(*args, **kwargs):  # pylint: disable=unused-argument
        return FakeResponse()

    monkeypatch.setattr(requests, 'get', fake_get)

    req = Requester('foo', 'bar', baseurl='http://dummy')
    with pytest.raises(JenkinsAPIException):
        req.get_and_confirm_status(
            url='http://dummy',
            params={'param': 'value'}
        )
