import mock
import unittest

from jenkinsapi import config
from jenkinsapi.job import Job
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.custom_exceptions import NoBuildData


class TestJob(unittest.TestCase):
    JOB_DATA = {
        "actions": [{
            "parameterDefinitions": [
            {
                "defaultParameterValue": {
                    "name": "param1",
                    "value": "test1"
                },
                "description": "",
                "name": "param1",
                "type": "StringParameterDefinition"
            },
            {
                "defaultParameterValue": {
                    "name": "param2",
                    "value": ""
                },
                "description": "",
                "name": "param2",
                "type": "StringParameterDefinition"
            }
            ]
        }],
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
            {"description": "Build stability: No recent builds failed.", "iconUrl": "health-80plus.png", "score": 100}
        ],
        "inQueue": False,
        "keepDependencies": False,
        "lastBuild": {"number": 4, "url": "http://halob:8080/job/foo/4/"},  # build running
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

    URL_DATA = {'http://halob:8080/job/foo/%s' % config.JENKINS_API: JOB_DATA}

    def fakeGetData(self, url, *args):
        try:
            return TestJob.URL_DATA[url]
        except KeyError:
            raise Exception("Missing data for %s" % url)

    @mock.patch.object(JenkinsBase, 'get_data', fakeGetData)
    def setUp(self):

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

        self.assertEquals(
            self.j.get_delete_url(), 'http://halob:8080/job/foo/doDelete')

        self.assertEquals(
            self.j.get_rename_url(), 'http://halob:8080/job/foo/doRename')

    def test_get_description(self):
        self.assertEquals(self.j.get_description(), 'test job')

    def test_get_build_triggerurl(self):
        self.assertEquals(
            self.j.get_build_triggerurl(), 'http://halob:8080/job/foo/buildWithParameters')

    def test_wrong__mk_json_from_build_parameters(self):
        with self.assertRaises(AssertionError) as ar:
            self.j._mk_json_from_build_parameters(build_params='bad parameter')

        self.assertEquals(
            ar.exception.message, 'Build parameters must be a dict')

    def test__mk_json_from_build_parameters(self):
        params = {'param1': 'value1', 'param2': 'value2'}
        ret = self.j.mk_json_from_build_parameters(build_params=params)
        self.assertTrue(isinstance(ret, str))
        self.assertEquals(ret,
                          '{"parameter": [{"name": "param2", "value": "value2"}, {"name": "param1", "value": "value1"}]}')

    def test_wrong_mk_json_from_build_parameters(self):
        with self.assertRaises(AssertionError) as ar:
            self.j.mk_json_from_build_parameters(build_params='bad parameter')

        self.assertEquals(
            ar.exception.message, 'Build parameters must be a dict')

    @mock.patch.object(JenkinsBase, 'get_data', fakeGetData)
    def test_wrong_field__build_id_for_type(self):
        with self.assertRaises(AssertionError):
            self.j._buildid_for_type('wrong')

    @mock.patch.object(JenkinsBase, 'get_data', fakeGetData)
    def test_get_last_good_buildnumber(self):
        ret = self.j.get_last_good_buildnumber()
        self.assertTrue(ret, 3)

    @mock.patch.object(JenkinsBase, 'get_data', fakeGetData)
    def test_get_last_stable_buildnumber(self):
        ret = self.j.get_last_stable_buildnumber()
        self.assertTrue(ret, 3)

    @mock.patch.object(JenkinsBase, 'get_data', fakeGetData)
    def test_get_last_failed_buildnumber(self):
        with self.assertRaises(NoBuildData):
            self.j.get_last_failed_buildnumber()

    @mock.patch.object(JenkinsBase, 'get_data', fakeGetData)
    def test_get_last_buildnumber(self):
        ret = self.j.get_last_buildnumber()
        self.assertEquals(ret, 4)

    @mock.patch.object(JenkinsBase, 'get_data', fakeGetData)
    def test_get_last_completed_buildnumber(self):
        ret = self.j.get_last_completed_buildnumber()
        self.assertEquals(ret, 3)

    def test_get_build_dict(self):
        ret = self.j.get_build_dict()
        self.assertTrue(isinstance(ret, dict))
        self.assertEquals(len(ret), 4)

    @mock.patch.object(Job, '_poll')
    def test_nobuilds_get_build_dict(self, _poll):
        # Bare minimum build dict, we only testing dissapearance of 'builds'
        _poll.return_value = {"name": "foo"}

        j = Job('http://halob:8080/job/foo/', 'foo', self.J)
        with self.assertRaises(NoBuildData):
            j.get_build_dict()

    def test_get_build_ids(self):
        # We don't want to deal with listreverseiterator here
        # So we convert result to a list
        ret = list(self.j.get_build_ids())
        self.assertTrue(isinstance(ret, list))
        self.assertEquals(len(ret), 4)

    @mock.patch.object(Job, '_poll')
    def test_nobuilds_get_revision_dict(self, _poll):
        # Bare minimum build dict, we only testing dissapearance of 'builds'
        _poll.return_value = {"name": "foo"}

        j = Job('http://halob:8080/job/foo/', 'foo', self.J)
        with self.assertRaises(NoBuildData):
            j.get_revision_dict()

    @mock.patch.object(Job, '_poll')
    def test_nobuilds_get_last_build(self, _poll):
        # Bare minimum build dict, we only testing dissapearance of 'builds'
        _poll.return_value = {"name": "foo"}

        j = Job('http://halob:8080/job/foo/', 'foo', self.J)
        with self.assertRaises(NoBuildData):
            j.get_last_build()

    @mock.patch.object(JenkinsBase, 'get_data')
    def test_empty_field__add_missing_builds(self, get_data):
        url = 'http://halob:8080/job/foo/%s' % config.JENKINS_API
        data = TestJob.URL_DATA[url].copy()
        data.update({'firstBuild': None})
        get_data.return_value = data
        j = Job('http://halob:8080/job/foo/', 'foo', self.J)
        initial_call_count = get_data.call_count
        j._add_missing_builds(data)
        self.assertEquals(get_data.call_count, initial_call_count)

    @mock.patch.object(JenkinsBase, 'get_data')
    def test_get_params(self, get_data):
        url = 'http://halob:8080/job/foo/%s' % config.JENKINS_API
        get_data.return_value = TestJob.URL_DATA[url].copy()
        j = Job('http://halob:8080/job/foo/', 'foo', self.J)
        params = list(j.get_params())
        self.assertEquals(len(params), 2)

    @mock.patch.object(JenkinsBase, 'get_data')
    def test_get_params_list(self, get_data):
        url = 'http://halob:8080/job/foo/%s' % config.JENKINS_API
        get_data.return_value = TestJob.URL_DATA[url].copy()
        j = Job('http://halob:8080/job/foo/', 'foo', self.J)

        params = j.get_params_list()

        self.assertIsInstance(params, list)
        self.assertEquals(len(params), 2)
        self.assertEquals(params, ['param1', 'param2'])

if __name__ == '__main__':
    unittest.main()
