import pytest

from jenkinsapi.plugins import Plugins
from jenkinsapi.utils.requester import Requester
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.job import Job
from jenkinsapi.custom_exceptions import JenkinsAPIException

DATA = {}
TWO_JOBS_DATA = {
    'jobs': [
        {'name': 'job_one',
         'url': 'http://localhost:8080/job/job_one',
         'color': 'blue'},
        {'name': 'job_two',
         'url': 'http://localhost:8080/job/job_two',
         'color': 'blue'},
    ]
}


@pytest.fixture(scope='function')
def jenkins(monkeypatch):
    def fake_poll(cls, tree=None):   # pylint: disable=unused-argument
        return {}

    monkeypatch.setattr(Jenkins, '_poll', fake_poll)

    return Jenkins('http://localhost:8080',
                   username='foouser', password='foopassword')


def test__clone(jenkins):
    cloned = jenkins._clone()
    assert id(cloned) != id(jenkins)
    assert cloned == jenkins


def test_stored_passwords(jenkins):
    assert jenkins.requester.password == 'foopassword'
    assert jenkins.requester.username == 'foouser'


def test_reload(monkeypatch):
    class FakeResponse(object):
        status_code = 200
        text = '{}'

    def fake_get_url(
            url,  # pylint: disable=unused-argument
            params=None,  # pylint: disable=unused-argument
            headers=None,  # pylint: disable=unused-argument
            allow_redirects=True,  # pylint: disable=unused-argument
            stream=False):  # pylint: disable=unused-argument

        return FakeResponse()

    monkeypatch.setattr(Requester, 'get_url', fake_get_url)
    mock_requester = Requester(username='foouser', password='foopassword')
    jenkins = Jenkins(
        'http://localhost:8080/',
        username='foouser', password='foopassword',
        requester=mock_requester)
    jenkins.poll()


def test_get_jobs_list(monkeypatch):
    def fake_jenkins_poll(cls, tree=None):  # pylint: disable=unused-argument
        return TWO_JOBS_DATA

    def fake_job_poll(cls, tree=None):  # pylint: disable=unused-argument
        return {}

    monkeypatch.setattr(JenkinsBase, '_poll', fake_jenkins_poll)
    monkeypatch.setattr(Jenkins, '_poll', fake_jenkins_poll)
    monkeypatch.setattr(Job, '_poll', fake_job_poll)

    jenkins = Jenkins('http://localhost:8080/',
                      username='foouser', password='foopassword')
    for idx, job_name in enumerate(jenkins.get_jobs_list()):
        assert job_name == TWO_JOBS_DATA['jobs'][idx]['name']

    for idx, job_name in enumerate(jenkins.jobs.keys()):
        assert job_name == TWO_JOBS_DATA['jobs'][idx]['name']


def test_create_new_job_fail(mocker, monkeypatch):
    def fake_jenkins_poll(cls, tree=None):  # pylint: disable=unused-argument
        return TWO_JOBS_DATA

    def fake_job_poll(cls, tree=None):  # pylint: disable=unused-argument
        return {}

    monkeypatch.setattr(JenkinsBase, '_poll', fake_jenkins_poll)
    monkeypatch.setattr(Jenkins, '_poll', fake_jenkins_poll)
    monkeypatch.setattr(Job, '_poll', fake_job_poll)

    mock_requester = Requester(username='foouser', password='foopassword')
    mock_requester.post_xml_and_confirm_status = mocker.MagicMock(
        return_value=''
    )

    jenkins = Jenkins('http://localhost:8080/',
                      username='foouser', password='foopassword',
                      requester=mock_requester)

    with pytest.raises(JenkinsAPIException) as ar:
        jenkins.create_job('job_new', None)

    assert 'Job XML config cannot be empty' in str(ar.value)


def test_get_jenkins_obj_from_url(mocker, monkeypatch):
    def fake_jenkins_poll(cls, tree=None):  # pylint: disable=unused-argument
        return TWO_JOBS_DATA

    def fake_job_poll(cls, tree=None):  # pylint: disable=unused-argument
        return {}

    monkeypatch.setattr(JenkinsBase, '_poll', fake_jenkins_poll)
    monkeypatch.setattr(Jenkins, '_poll', fake_jenkins_poll)
    monkeypatch.setattr(Job, '_poll', fake_job_poll)

    mock_requester = Requester(username='foouser', password='foopassword')
    mock_requester.post_xml_and_confirm_status = mocker.MagicMock(
        return_value=''
    )

    jenkins = Jenkins('http://localhost:8080/',
                      username='foouser', password='foopassword',
                      requester=mock_requester)

    new_jenkins = jenkins.get_jenkins_obj_from_url('http://localhost:8080/')
    assert new_jenkins == jenkins

    new_jenkins = jenkins.get_jenkins_obj_from_url('http://localhost:8080/foo')
    assert new_jenkins != jenkins


def test_get_jenkins_obj(mocker, monkeypatch):
    def fake_jenkins_poll(cls, tree=None):  # pylint: disable=unused-argument
        return TWO_JOBS_DATA

    def fake_job_poll(cls, tree=None):  # pylint: disable=unused-argument
        return {}

    monkeypatch.setattr(JenkinsBase, '_poll', fake_jenkins_poll)
    monkeypatch.setattr(Jenkins, '_poll', fake_jenkins_poll)
    monkeypatch.setattr(Job, '_poll', fake_job_poll)

    mock_requester = Requester(username='foouser', password='foopassword')
    mock_requester.post_xml_and_confirm_status = mocker.MagicMock(
        return_value=''
    )

    jenkins = Jenkins('http://localhost:8080/',
                      username='foouser', password='foopassword',
                      requester=mock_requester)

    new_jenkins = jenkins.get_jenkins_obj()
    assert new_jenkins == jenkins


def test_get_version(monkeypatch):
    class MockResponse(object):
        def __init__(self):
            self.headers = {}
            self.headers['X-Jenkins'] = '1.542'

    def fake_poll(cls, tree=None):   # pylint: disable=unused-argument
        return {}

    monkeypatch.setattr(Jenkins, '_poll', fake_poll)

    def fake_get(cls, *arga, **kwargs):  # pylint: disable=unused-argument
        return MockResponse()

    monkeypatch.setattr(Requester, 'get_and_confirm_status', fake_get)

    jenkins = Jenkins('http://foobar:8080/',
                      username='foouser', password='foopassword')
    assert jenkins.version == '1.542'


def test_get_version_nonexistent(mocker):
    class MockResponse(object):
        status_code = 200
        headers = {}
        text = '{}'

    mock_requester = Requester(username='foouser', password='foopassword')
    mock_requester.get_url = mocker.MagicMock(
        return_value=MockResponse()
    )
    jenkins = Jenkins('http://localhost:8080',
                      username='foouser', password='foopassword',
                      requester=mock_requester)
    assert jenkins.version == '0.0'


def test_get_master_data(mocker):
    class MockResponse(object):
        status_code = 200
        headers = {}
        text = '{}'

    mock_requester = Requester(username='foouser', password='foopassword')
    mock_requester.get_url = mocker.MagicMock(
        return_value=MockResponse()
    )
    jenkins = Jenkins('http://localhost:808',
                      username='foouser', password='foopassword',
                      requester=mock_requester)
    jenkins.get_data = mocker.MagicMock(
        return_value={
            "busyExecutors": 59,
            "totalExecutors": 75
        }
    )

    data = jenkins.get_master_data()
    assert data['busyExecutors'] == 59
    assert data['totalExecutors'] == 75


def test_get_create_url(monkeypatch):
    def fake_poll(cls, tree=None):  # pylint: disable=unused-argument
        return {}

    monkeypatch.setattr(Jenkins, '_poll', fake_poll)
    # Jenkins URL w/o slash
    jenkins = Jenkins('http://localhost:8080',
                      username='foouser', password='foopassword')
    assert jenkins.get_create_url() == 'http://localhost:8080/createItem'
    # Jenkins URL w/ slash
    jenkins = Jenkins('http://localhost:8080/',
                      username='foouser', password='foopassword')
    assert jenkins.get_create_url() == 'http://localhost:8080/createItem'


def test_has_plugin(monkeypatch):
    def fake_poll(cls, tree=None):  # pylint: disable=unused-argument
        return {}

    monkeypatch.setattr(Jenkins, '_poll', fake_poll)

    def fake_plugin_poll(cls, tree=None):  # pylint: disable=unused-argument
        return {
            'plugins': [
                {
                    'deleted': False, 'hasUpdate': True, 'downgradable': False,
                    'dependencies': [{}, {}, {}, {}],
                    'longName': 'Jenkins Subversion Plug-in', 'active': True,
                    'shortName': 'subversion', 'backupVersion': None,
                    'url': 'http://wiki.jenkins-ci.org/'
                           'display/JENKINS/Subversion+Plugin',
                    'enabled': True, 'pinned': False, 'version': '1.45',
                    'supportsDynamicLoad': 'MAYBE', 'bundled': True
                }
            ]
        }

    monkeypatch.setattr(Plugins, '_poll', fake_plugin_poll)

    jenkins = Jenkins('http://localhost:8080/',
                      username='foouser', password='foopassword')
    assert jenkins.has_plugin('subversion') is True
