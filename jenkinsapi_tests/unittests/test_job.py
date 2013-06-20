import mock
import unittest
import datetime

from jenkinsapi.job import Job
from jenkinsapi.exceptions import NoBuildData

class TestJob(unittest.TestCase):

    DATA = {"actions": [],
            "description": "test job",
            "displayName": "foo",
            "displayNameOrNull": None,
            "name": "foo",
            "url": "http://halob:8080/job/foo/",
            "buildable": True,
            "builds": [{"number": 3, "url": "http://halob:8080/job/foo/3/"},
           {"number": 2, "url": "http://halob:8080/job/foo/2/"},
                {"number": 1, "url": "http://halob:8080/job/foo/1/"}],
            "color": "blue",
            "firstBuild": {"number": 1, "url": "http://halob:8080/job/foo/1/"},
            "healthReport": [{"description": "Build stability: No recent builds failed.",
                             "iconUrl": "health-80plus.png", "score": 100}],
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
            "upstreamProjects": []}

    @mock.patch.object(Job, '_poll')
    def setUp(self, _poll):
        _poll.return_value = self.DATA

        # def __init__( self, url, name, jenkins_obj ):

        self.J = mock.MagicMock()  # Jenkins object
        self.j = Job('http://halob:8080/job/foo/', 'foo', self.J)

    def testRepr(self):
        # Can we produce a repr string for this object
        self.assertEquals(repr(self.j), '<jenkinsapi.job.Job foo>')

    def testName(self):
        with self.assertRaises(AttributeError):
        	self.j.id()
    	self.assertEquals(self.j.name, 'foo')

    def testNextBuildNumber(self):
        self.assertEquals(self.j.get_next_build_number(), 4)

    def test_special_urls(self):
        self.assertEquals(self.j.baseurl, 'http://halob:8080/job/foo')

        self.assertEquals(self.j.get_delete_url(), 'http://halob:8080/job/foo/doDelete')

        self.assertEquals(self.j.get_rename_url(), 'http://halob:8080/job/foo/doRename')

    def test_get_description(self):
        self.assertEquals(self.j.get_description(), 'test job')

    def test_get_build_triggerurl(self):
        self.assertEquals(self.j.get_build_triggerurl(), 'http://halob:8080/job/foo/build')

    def test_wrong__mk_json_from_build_parameters(self):
        with self.assertRaises(AssertionError) as ar:
            self.j._mk_json_from_build_parameters(build_params='bad parameter')

        self.assertEquals(ar.exception.message, 'Build parameters must be a dict')

    def test__mk_json_from_build_parameters(self):
        params = {'param1': 'value1', 'param2': 'value2'}
        ret = self.j._mk_json_from_build_parameters(build_params=params)
        self.assertTrue(isinstance(ret, dict))
        self.assertTrue(isinstance(ret.get('parameter'), list))
        self.assertEquals(len(ret.get('parameter')), 2)

    def test_wrong_mk_json_from_build_parameters(self):
        with self.assertRaises(AssertionError) as ar:
            self.j.mk_json_from_build_parameters(build_params='bad parameter')

        self.assertEquals(ar.exception.message, 'Build parameters must be a dict')

    def test__mk_json_from_build_parameters(self):
        params = {'param1': 'value1', 'param2': 'value2'}
        ret = self.j.mk_json_from_build_parameters(build_params=params)
        self.assertTrue(isinstance(ret, str))
        self.assertEquals(ret, 
                '{"parameter": [{"name": "param2", "value": "value2"}, {"name": "param1", "value": "value1"}]}')

    def test_wrong_field__build_id_for_type(self):
        with self.assertRaises(AssertionError) as ar:
            self.j._buildid_for_type('wrong')

    def test_get_last_good_buildnumber(self):
        ret = self.j.get_last_good_buildnumber()
        self.assertTrue(ret, 3)

    def test_get_last_failed_buildnumber(self):
        ret = self.j.get_last_failed_buildnumber()
        self.assertEquals(ret, None)

    def test_get_last_buildnumber(self):
        ret = self.j.get_last_buildnumber()
        self.assertEquals(ret, 3)

    def test_get_last_completed_buildnumber(self):
        ret = self.j.get_last_completed_buildnumber()
        self.assertEquals(ret, 3)

    def test_get_build_dict(self):
        ret = self.j.get_build_dict()
        self.assertTrue(isinstance(ret, dict))
        self.assertEquals(len(ret), 3)

    @mock.patch.object(Job, '_poll')
    def test_nobuilds_get_build_dict(self, _poll):
        # Bare minimum build dict, we only testing dissapearance of 'builds'
        _poll.return_value = {"name": "foo"}

        j = Job('http://halob:8080/job/foo/', 'foo', self.J)
        with self.assertRaises(NoBuildData) as nbd:
            ret = j.get_build_dict()

    def test_get_build_ids(self):
        # We don't want to deal with listreverseiterator here
        # So we convert result to a list
        ret = list(self.j.get_build_ids())
        self.assertTrue(isinstance(ret, list))
        self.assertEquals(len(ret), 3)

    @mock.patch.object(Job, '_poll')
    def test_nobuilds_get_revision_dict(self, _poll):
        # Bare minimum build dict, we only testing dissapearance of 'builds'
        _poll.return_value = {"name": "foo"}

        j = Job('http://halob:8080/job/foo/', 'foo', self.J)
        with self.assertRaises(NoBuildData) as nbd:
            ret = j.get_revision_dict()


if __name__ == '__main__':
    unittest.main()
