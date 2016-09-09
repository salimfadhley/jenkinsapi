import mock
import json
# To run unittests on python 2.6 please use unittest2 library
try:
    import unittest2 as unittest
except ImportError:
    import unittest

import jenkinsapi
from jenkinsapi import config
from jenkinsapi.job import Job
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.custom_exceptions import NoBuildData


class TestJob(unittest.TestCase):
    JOB_DATA = {
        "actions": [{
            "parameterDefinitions": [{
                "defaultParameterValue": {
                    "name": "param1",
                    "value": "test1"
                },
                "description": "",
                "name": "param1",
                "type": "StringParameterDefinition"
            }, {
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
        # allBuilds is not present in job dict returned by Jenkins
        # it is inserted here to test _add_missing_builds()
        "allBuilds": [
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
        # build running
        "lastBuild": {"number": 4, "url": "http://halob:8080/job/foo/4/"},
        "lastCompletedBuild": {"number": 3,
                               "url": "http://halob:8080/job/foo/3/"},
        "lastFailedBuild": None,
        "lastStableBuild": {"number": 3,
                            "url": "http://halob:8080/job/foo/3/"},
        "lastSuccessfulBuild": {"number": 3,
                                "url": "http://halob:8080/job/foo/3/"},
        "lastUnstableBuild": None,
        "lastUnsuccessfulBuild": None,
        "nextBuildNumber": 4,
        "property": [],
        "queueItem": None,
        "concurrentBuild": False,
        # test1 job exists, test2 does not
        "downstreamProjects": [{'name': 'test1'}, {'name': 'test2'}],
        "scm": {},
        "upstreamProjects": []
    }

    URL_DATA = {'http://halob:8080/job/foo/%s' % config.JENKINS_API: JOB_DATA}

    def fakeGetData(self, url, **args):
        try:
            return TestJob.URL_DATA[url]
        except KeyError:
            raise Exception("Missing data for %s" % url)

    def fakeGetDataTree(self, url, **args):
        try:
            if 'builds' in args['tree']:
                return {'builds': TestJob.URL_DATA[url]['builds']}
            else:
                return {'lastBuild': TestJob.URL_DATA[url]['lastBuild']}
        except KeyError:
            raise Exception("Missing data for %s" % url)

    def fake_get_data_tree_empty(self, url, **args):
        return {}

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
        self.assertEquals(self.j.get_build_triggerurl(),
                          'http://halob:8080/job/foo/buildWithParameters')

    def test_wrong__mk_json_from_build_parameters(self):
        with self.assertRaises(AssertionError) as ar:
            self.j._mk_json_from_build_parameters(build_params='bad parameter')

        self.assertEquals(
            str(ar.exception), 'Build parameters must be a dict')

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

    @mock.patch.object(JenkinsBase, 'get_data', fakeGetDataTree)
    def test_get_build_dict(self):
        ret = self.j.get_build_dict()
        self.assertTrue(isinstance(ret, dict))
        self.assertEquals(len(ret), 4)

    @mock.patch.object(JenkinsBase, 'get_data', fake_get_data_tree_empty)
    def test_nobuilds_get_build_dict(self):
        j = Job('http://halob:8080/job/foo/', 'foo', self.J)
        with self.assertRaises(NoBuildData):
            j.get_build_dict()

    @mock.patch.object(JenkinsBase, 'get_data', fakeGetDataTree)
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
    def test__add_missing_builds_not_all_loaded(self, get_data):
        url = 'http://halob:8080/job/foo/%s' % config.JENKINS_API
        data = TestJob.URL_DATA[url].copy()
        get_data.return_value = data
        j = Job('http://halob:8080/job/foo/', 'foo', self.J)
        # to test this function we change data to not have one build
        # and set it to mark that firstBuild was not loaded
        # in that condition function will call j.get_data
        # and will use syntetic field 'allBuilds' to
        # repopulate 'builds' field with all builds
        mock_data = TestJob.URL_DATA[url].copy()
        mock_data['firstBuild'] = {'number': 1}
        del mock_data['builds'][-1]
        self.assertEquals(len(mock_data['builds']), 2)
        new_data = j._add_missing_builds(mock_data)
        self.assertEquals(len(new_data['builds']), 3)

    @mock.patch.object(JenkinsBase, 'get_data')
    def test__add_missing_builds_no_first_build(self, get_data):
        url = 'http://halob:8080/job/foo/%s' % config.JENKINS_API
        data = TestJob.URL_DATA[url].copy()
        get_data.return_value = data
        j = Job('http://halob:8080/job/foo/', 'foo', self.J)
        initial_call_count = get_data.call_count
        mock_data = TestJob.URL_DATA[url].copy()
        mock_data['firstBuild'] = None
        j._add_missing_builds(mock_data)
        self.assertEquals(initial_call_count, get_data.call_count)

    @mock.patch.object(JenkinsBase, 'get_data')
    def test__add_missing_builds_no_builds(self, get_data):
        url = 'http://halob:8080/job/foo/%s' % config.JENKINS_API
        data = TestJob.URL_DATA[url].copy()
        get_data.return_value = data
        j = Job('http://halob:8080/job/foo/', 'foo', self.J)
        initial_call_count = get_data.call_count
        mock_data = TestJob.URL_DATA[url].copy()
        mock_data['builds'] = None
        j._add_missing_builds(mock_data)
        self.assertEquals(initial_call_count, get_data.call_count)

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

        self.assertTrue(j.has_params())
        params = j.get_params_list()

        self.assertIsInstance(params, list)
        self.assertEquals(len(params), 2)
        self.assertEquals(params, ['param1', 'param2'])

    @mock.patch.object(JenkinsBase, 'get_data', fakeGetDataTree)
    # @mock.patch.object(JenkinsBase, 'get_data', fakeGetLastBuild)
    def test_get_build(self):
        buildnumber = 1
        with mock.patch('jenkinsapi.job.Build') as build_mock:
            instance = build_mock.return_value
            build = self.j.get_build(buildnumber)
            self.assertEquals(build, instance)
            build_mock.assert_called_with('http://halob:8080/job/foo/1/',
                                          buildnumber, job=self.j)

    @mock.patch.object(JenkinsBase, 'get_data', fakeGetDataTree)
    def test_get_build_metadata(self):
        buildnumber = 1
        with mock.patch('jenkinsapi.job.Build') as build_mock:
            instance = build_mock.return_value
            build = self.j.get_build_metadata(buildnumber)
            self.assertEquals(build, instance)
            build_mock.assert_called_with('http://halob:8080/job/foo/1/',
                                          buildnumber, job=self.j, depth=0)

    def assertJsonEqual(self, jsonA, jsonB, msg=None):
        A = json.loads(jsonA)
        B = json.loads(jsonB)
        self.assertEqual(
            A,
            B,
            msg
        )

    def test_get_json_for_single_param(self):
        params = {"B": "one two three"}
        expected = '{"parameter": {"name": "B", "value": "one two three"}, "statusCode": "303", "redirectTo": "."}'
        self.assertJsonEqual(
            Job.mk_json_from_build_parameters(params),
            expected
        )

    def test_get_json_for_many_params(self):
        params = {"B": "Honey", "A": "Boo", "C": 2}
        expected = '{"parameter": [{"name": "A", "value": "Boo"}, {"name": "B", "value": "Honey"}, {"name": "C", "value": "2"}], "statusCode": "303", "redirectTo": "."}'

        self.assertJsonEqual(
            Job.mk_json_from_build_parameters(params),
            expected
        )

    def test__mk_json_from_build_parameters(self):
        params = {'param1': 'value1', 'param2': 'value2'}
        result = self.j._mk_json_from_build_parameters(build_params=params)
        self.assertTrue(isinstance(result, dict))

        self.assertEquals(
            result,
            {"parameter": [{"name": "param1", "value": "value1"}, {
                "name": "param2", "value": "value2"}]}
        )

    def test_wrong_mk_json_from_build_parameters(self):
        with self.assertRaises(AssertionError) as ar:
            self.j.mk_json_from_build_parameters(build_params='bad parameter')

        self.assertEquals(
            str(ar.exception), 'Build parameters must be a dict')

    def test_get_build_by_params(self):
        build_params = {
            'param1': 'value1'
        }
        get_params_mock = mock.Mock(side_effect=({}, {}, build_params))
        build_mock = mock.Mock(get_params=get_params_mock)
        with mock.patch.object(self.j, 'get_first_buildnumber', return_value=1), \
                mock.patch.object(self.j, 'get_last_buildnumber', return_value=3), \
                mock.patch.object(self.j, 'get_build', return_value=build_mock) as get_build_mock:
            result = self.j.get_build_by_params(build_params)
            assert get_build_mock.call_count == 3
            assert get_params_mock.call_count == 3
            assert result == build_mock


if __name__ == '__main__':
    unittest.main()
