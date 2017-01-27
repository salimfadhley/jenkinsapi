from __future__ import print_function
import requests
from jenkinsapi.utils.crumb_requester import CrumbRequester


def test_crumb_get_url(monkeypatch):
    def fake_get(*args, **kwargs):  # pylint: disable=unused-argument
        return 'SUCCESS'

    def fake_crumb(self): # pylint: disable=unused-argument
        return {'crumbName': 'crumbValue'}

    monkeypatch.setattr(requests, 'get', fake_get)
    monkeypatch.setattr(CrumbRequester, '_get_crumb_data', fake_crumb)
    req = CrumbRequester('foo', 'bar', baseurl='http://dummy')

    response = req.get_url(
        'http://dummy',
        params={'param': 'value'},
        headers=None)

    assert response == 'SUCCESS'
    assert req._last_crumb_data is not None


def test_get_url_post(monkeypatch):
    def fake_post(*args, **kwargs):  # pylint: disable=unused-argument
        return 'SUCCESS'

    def fake_crumb(self): # pylint: disable=unused-argument
        return {'crumbName': 'crumbValue'}

    monkeypatch.setattr(requests, 'post', fake_post)
    monkeypatch.setattr(CrumbRequester, '_get_crumb_data', fake_crumb)
    req = CrumbRequester('foo', 'bar', baseurl='http://dummy')

    response = req.post_url(
        'http://dummy',
        params={'param': 'value'},
        headers=None)

    assert response == 'SUCCESS'
    assert req._last_crumb_data is not None
