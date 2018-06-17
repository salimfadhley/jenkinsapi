import mock
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.view import View
from jenkinsapi.job import Job
from jenkinsapi.custom_exceptions import NotFound


class TestView(unittest.TestCase):

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

    @mock.patch.object(Job, '_poll')
    @mock.patch.object(View, '_poll')
    def setUp(self, _view_poll, _job_poll):
        _view_poll.return_value = self.DATA
        _job_poll.return_value = self.JOB_DATA

        self.jenkins = mock.MagicMock()
        self.jenkins.has_job.return_value = False
        self.view = View('http://localhost:800/view/FodFanFo', 'FodFanFo', self.jenkins)

    def test_returns_name_when_repr_is_called(self):
        assert repr(self.view) == 'FodFanFo'

    def test_returns_name_when_str_method_called(self):
        assert str(self.view) == 'FodFanFo'

    def test_raises_error_when_is_called(self):
        with self.assertRaises(AttributeError):
            self.view.id()

    def test_returns_name_when_name_property_is_called(self):
        assert self.view.name == 'FodFanFo'

    @mock.patch.object(JenkinsBase, '_poll')
    def test_iteritems(self, _poll):
        _poll.return_value = self.JOB_DATA
        for job_name, job_obj in self.view.iteritems():
            self.assertTrue(isinstance(job_obj, Job))

    def test_returns_dict_of_job_info_when_job_dict_method_called(self):
        jobs = self.view.get_job_dict()
        assert jobs == {
            'foo': 'http://halob:8080/job/foo/',
            'test_jenkinsapi': 'http://halob:8080/job/test_jenkinsapi/'
        }

    def test_returns_len_when_len_is_called(self):
        assert len(self.view) == 2

    # We have to re-patch JenkinsBase here because by the time
    # it get to create Job, MagicMock will already expire
    @mock.patch.object(JenkinsBase, '_poll')
    def test_getitem(self, _poll):
        _poll.return_value = self.JOB_DATA
        self.assertTrue(isinstance(self.view['foo'], Job))

    def test_delete(self):
        self.view.delete()
        self.assertTrue(self.view.deleted)

    def test_get_job_url(self):
        self.assertEquals(
            self.view.get_job_url('foo'),
            'http://halob:8080/job/foo/')

    def test_wrong_get_job_url(self):
        with self.assertRaises(NotFound):
            self.view.get_job_url('bar')

    # We have to re-patch JenkinsBase here because by the time
    # it get to create Job, MagicMock will already expire
    @mock.patch.object(JenkinsBase, '_poll')
    @mock.patch.object(View, '_poll')
    def test_add_job(self, _poll, _view_poll):
        _poll.return_value = self.DATA
        _view_poll.return_value = self.DATA
        J = mock.MagicMock()  # Jenkins object
        J.has_job.return_value = True
        v = View('http://localhost:800/view/FodFanFo', 'FodFanFo', self.jenkins)

        result = v.add_job('bar')
        self.assertTrue(result)

    # We have to re-patch JenkinsBase here because by the time
    # it get to create Job, MagicMock will already expire
    @mock.patch.object(View, 'get_jenkins_obj')
    def test_returns_false_when_adding_wrong_job(self, _get_jenkins):

        class SelfPatchJenkins(object):
            def has_job(self, job_name):
                return False

            def get_jenkins_obj_from_url(self, url):
                return self

        _get_jenkins.return_value = SelfPatchJenkins()
        result = self.view.add_job('bar')

        assert result is False

    def test_returns_false_when_add_existing_job(self):
        result = self.view.add_job('foo')

        assert result is False

    def test_get_nested_view_dict(self):
        result = self.view.get_nested_view_dict()

        assert isinstance(result, dict)
        assert len(result) == 0


if __name__ == '__main__':
    unittest.main()
