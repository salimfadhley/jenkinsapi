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

        # def __init__(self, url, name, jenkins_obj)
        self.J = mock.MagicMock()  # Jenkins object
        self.J.has_job.return_value = False
        self.v = View('http://localhost:800/view/FodFanFo', 'FodFanFo', self.J)

    def testRepr(self):
        # Can we produce a repr string for this object
        repr(self.v)

    def testName(self):
        with self.assertRaises(AttributeError):
            self.v.id()
        self.assertEquals(self.v.name, 'FodFanFo')

    @mock.patch.object(JenkinsBase, '_poll')
    def test_iteritems(self, _poll):
        _poll.return_value = self.JOB_DATA
        for job_name, job_obj in self.v.iteritems():
            self.assertTrue(isinstance(job_obj, Job))

    def test_get_job_dict(self):
        jobs = self.v.get_job_dict()
        self.assertEquals(jobs, {
            'foo': 'http://halob:8080/job/foo/',
            'test_jenkinsapi': 'http://halob:8080/job/test_jenkinsapi/'})

    def test_len(self):
        self.assertEquals(len(self.v), 2)

    # We have to re-patch JenkinsBase here because by the time
    # it get to create Job, MagicMock will already expire
    @mock.patch.object(JenkinsBase, '_poll')
    def test_getitem(self, _poll):
        _poll.return_value = self.JOB_DATA
        self.assertTrue(isinstance(self.v['foo'], Job))

    def test_delete(self):
        self.v.delete()
        self.assertTrue(self.v.deleted)

    def test_get_job_url(self):
        self.assertEquals(
            self.v.get_job_url('foo'),
            'http://halob:8080/job/foo/')

    def test_wrong_get_job_url(self):
        with self.assertRaises(NotFound):
            self.v.get_job_url('bar')

    # We have to re-patch JenkinsBase here because by the time
    # it get to create Job, MagicMock will already expire
    @mock.patch.object(JenkinsBase, '_poll')
    @mock.patch.object(View, '_poll')
    def test_add_job(self, _poll, _view_poll):
        _poll.return_value = self.DATA
        _view_poll.return_value = self.DATA
        J = mock.MagicMock()  # Jenkins object
        J.has_job.return_value = True
        v = View('http://localhost:800/view/FodFanFo', 'FodFanFo', self.J)

        result = v.add_job('bar')
        self.assertTrue(result)

    class SelfPatchJenkins(object):

        def has_job(self, job_name):
            return False

        def get_jenkins_obj_from_url(self, url):
            return self

    # We have to re-patch JenkinsBase here because by the time
    # it get to create Job, MagicMock will already expire
    @mock.patch.object(View, 'get_jenkins_obj')
    def test_add_wrong_job(self, _get_jenkins):
        _get_jenkins.return_value = TestView.SelfPatchJenkins()
        result = self.v.add_job('bar')
        self.assertFalse(result)

    def test_add_existing_job(self):
        result = self.v.add_job('foo')
        self.assertFalse(result)

    def test_get_nested_view_dict(self):
        result = self.v.get_nested_view_dict()
        self.assertTrue(isinstance(result, dict))
        self.assertEquals(len(result), 0)


if __name__ == '__main__':
    unittest.main()
