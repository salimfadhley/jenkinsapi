import mock

import pytest

from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.view import View
from jenkinsapi.job import Job
from jenkinsapi.custom_exceptions import NotFound

DATA = {'description': 'Important Shizz',
        'jobs': [
            {'color': 'blue',
             'name': 'foo',
             'url': 'http://halob:8080/job/foo/'},
            {'color': 'red',
             'name': 'test_jenkinsapi',
             'url': 'http://halob:8080/job/test_jenkinsapi/'}
        ],
        'name': 'FodFanFo',
        'property': [],
        'url': 'http://halob:8080/view/FodFanFo/'}

JOB_DATA = {
    "actions": [],
    "description": "test job",
    "displayName": "foo",
    "displayNameOrNull": None,
    "name": "foo",
    "url": "http://halob:8080/job/foo/",
    "buildable": True,
    "builds": [
        {"number": 3, "url": "http://halob:8080/job/foo/3/"},
        {"number": 2, "url": "http://halob:8080/job/foo/2/"},
        {"number": 1, "url": "http://halob:8080/job/foo/1/"}
    ],
    "color": "blue",
    "firstBuild": {"number": 1, "url": "http://halob:8080/job/foo/1/"},
    "healthReport": [
        {"description": "Build stability: No recent builds failed.",
         "iconUrl": "health-80plus.png", "score": 100}
    ],
    "inQueue": False,
    "keepDependencies": False,
    "lastBuild": {"number": 3, "url": "http://halob:8080/job/foo/3/"},
    "lastCompletedBuild": {"number": 3, "url": "http://halob:8080/job/foo/3/"},
    "lastFailedBuild": None,
    "lastStableBuild": {"number": 3, "url": "http://halob:8080/job/foo/3/"},
    "lastSuccessfulBuild": {"number": 3, "url": "http://halob:8080/job/foo/3/"},
    "lastUnstableBuild": None,
    "lastUnsuccessfulBuild": None,
    "nextBuildNumber": 4,
    "property": [],
    "queueItem": None,
    "concurrentBuild": False,
    "downstreamProjects": [],
    "scm": {},
    "upstreamProjects": []
}


@pytest.fixture
def jenkins():
    jenkins = mock.MagicMock()
    jenkins.has_job.return_value = False
    return jenkins


@mock.patch.object(Job, '_poll')
@mock.patch.object(View, '_poll')
@pytest.fixture
def view(_view_poll, _job_poll, jenkins):
    _view_poll.return_value = DATA
    _job_poll.return_value = JOB_DATA
    return View('http://localhost:800/view/FodFanFo',
                'FodFanFo',
                jenkins)


class TestView:

    def test_returns_name_when_repr_is_called(self, view):
        assert repr(view) == 'FodFanFo'

    def test_returns_name_when_str_method_called(self, view):
        assert str(view) == 'FodFanFo'

    def test_raises_error_when_is_called(self, view):
        with pytest.raises(AttributeError):
            view.id()

    def test_returns_name_when_name_property_is_called(self, view):
        assert view.name == 'FodFanFo'

    @mock.patch.object(JenkinsBase, '_poll')
    def test_iteritems(self, _poll, view):
        _poll.return_value = JOB_DATA
        for job_name, job_obj in view.iteritems():
            assert isinstance(job_obj, Job)

    def test_returns_dict_of_job_info_when_job_dict_method_called(self, view):
        jobs = view.get_job_dict()

        assert jobs == {
            'foo': 'http://halob:8080/job/foo/',
            'test_jenkinsapi': 'http://halob:8080/job/test_jenkinsapi/'
        }

    def test_returns_len_when_len_is_called(self, view):
        assert len(view) == 2

    @mock.patch.object(JenkinsBase, '_poll')
    def test_getitem(self, _poll, view):
        _poll.return_value = JOB_DATA

        assert isinstance(view['foo'], Job)

    def test_sets_delete_to_true_when_deleted(self, view):
        view.delete()

        assert view.deleted

    def test_returns_url_when_get_job_url_is_called(self, view):
        url = view.get_job_url('foo')

        assert url == 'http://halob:8080/job/foo/'

    def test_raises_not_found_when_get_job_url_is_invalid(self, view):
        with pytest.raises(NotFound):
            view.get_job_url('bar')

    @mock.patch.object(JenkinsBase, '_poll')
    @mock.patch.object(View, '_poll')
    def test_add_job(self, _poll, _view_poll, view):
        _poll.return_value = DATA
        _view_poll.return_value = DATA

        result = view.add_job('bar')

        assert result is True

    @mock.patch.object(View, 'get_jenkins_obj')
    def test_returns_false_when_adding_wrong_job(self, _get_jenkins, view):

        class SelfPatchJenkins(object):
            def has_job(self, job_name):
                return False

            def get_jenkins_obj_from_url(self, url):
                return self

        _get_jenkins.return_value = SelfPatchJenkins()
        result = view.add_job('bar')

        assert result is False

    def test_returns_false_when_add_existing_job(self, view):
        result = view.add_job('foo')

        assert result is False

    def test_get_nested_view_dict(self, view):
        result = view.get_nested_view_dict()

        assert isinstance(result, dict)
        assert len(result) == 0


class TestKeys:

    def test_returns_key_when_called(self, view):
        keys = view.keys()

        assert ['foo', 'test_jenkinsapi'] == list(keys)
