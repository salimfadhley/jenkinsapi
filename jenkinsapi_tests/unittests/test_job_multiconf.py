# import mock
# import unittest

# from jenkinsapi.job import Job
# from jenkinsapi.jenkinsbase import JenkinsBase
# from jenkinsapi.custom_exceptions import NoBuildData


# class TestMultiConfigJob(unittest.TestCase):
#     JOB_DATA = {'actions': [{'causes': [{'shortDescription': 'Started by user anonymous',
#                           'userId': None,
#                           'userName': 'anonymous'}]}],
#  'artifacts': [],
#  'building': False,
#  'builtOn': '',
#  'changeSet': {'items': [], 'kind': None},
#  'culprits': [],
#  'description': None,
#  'duration': 1042,
#  'estimatedDuration': 1055,
#  'executor': None,
#  'fullDisplayName': 'test_multiconf0 #16',
#  'id': '2013-07-17_00-39-50',
#  'keepLog': False,
#  'number': 16,
#  'result': 'SUCCESS',
#  'runs': [{'number': 10,
#            'url': 'http://halob:8080/job/test_multiconf0/./a=1,b=a/10/'},
#           {'number': 10,
#            'url': 'http://halob:8080/job/test_multiconf0/./a=1,b=b/10/'},
#           {'number': 10,
#            'url': 'http://halob:8080/job/test_multiconf0/./a=1,b=c/10/'},
#           {'number': 10,
#            'url': 'http://halob:8080/job/test_multiconf0/./a=2,b=a/10/'},
#           {'number': 10,
#            'url': 'http://halob:8080/job/test_multiconf0/./a=2,b=b/10/'},
#           {'number': 10,
#            'url': 'http://halob:8080/job/test_multiconf0/./a=2,b=c/10/'},
#           {'number': 10,
#            'url': 'http://halob:8080/job/test_multiconf0/./a=3,b=a/10/'},
#           {'number': 10,
#            'url': 'http://halob:8080/job/test_multiconf0/./a=3,b=b/10/'},
#           {'number': 10,
#            'url': 'http://halob:8080/job/test_multiconf0/./a=3,b=c/10/'},
#           {'number': 16,
#            'url': 'http://halob:8080/job/test_multiconf0/./a=q,b=x/16/'},
#           {'number': 16,
#            'url': 'http://halob:8080/job/test_multiconf0/./a=q,b=y/16/'},
#           {'number': 16,
#            'url': 'http://halob:8080/job/test_multiconf0/./a=q,b=z/16/'},
#           {'number': 16,
#            'url': 'http://halob:8080/job/test_multiconf0/./a=r,b=x/16/'},
#           {'number': 16,
#            'url': 'http://halob:8080/job/test_multiconf0/./a=r,b=y/16/'},
#           {'number': 16,
#            'url': 'http://halob:8080/job/test_multiconf0/./a=r,b=z/16/'},
#           {'number': 16,
#            'url': 'http://halob:8080/job/test_multiconf0/./a=s,b=x/16/'},
#           {'number': 16,
#            'url': 'http://halob:8080/job/test_multiconf0/./a=s,b=y/16/'},
#           {'number': 16,
#            'url': 'http://halob:8080/job/test_multiconf0/./a=s,b=z/16/'}],
#  'timestamp': 1374017990735,
#  'url': 'http://halob:8080/job/test_multiconf0/16/'}


#     URL_DATA = {'http://halob:8080/job/foo/api/python/':JOB_DATA}

#     def fakeGetData(self, url, *args):
#         try:
#             return TestJob.URL_DATA[url]
#         except KeyError:
#             raise Exception("Missing data for %s" % url)

#     @mock.patch.object(JenkinsBase, 'get_data', fakeGetData)
#     def setUp(self):

#         self.J = mock.MagicMock()  # Jenkins object
#         self.j = Job('http://halob:8080/job/foo/', 'foo', self.J)

#     def testRepr(self):
#         # Can we produce a repr string for this object
#         self.assertEquals(repr(self.j), '<jenkinsapi.job.Job foo>')

#     def testName(self):
#         with self.assertRaises(AttributeError):
#             self.j.id()
#         self.assertEquals(self.j.name, 'foo')

#     def testNextBuildNumber(self):
#         self.assertEquals(self.j.get_next_build_number(), 4)

#     def test_special_urls(self):
#         self.assertEquals(self.j.baseurl, 'http://halob:8080/job/foo')

#         self.assertEquals(
#             self.j.get_delete_url(), 'http://halob:8080/job/foo/doDelete')

#         self.assertEquals(
#             self.j.get_rename_url(), 'http://halob:8080/job/foo/doRename')

#     def test_get_description(self):
#         self.assertEquals(self.j.get_description(), 'test job')

#     def test_get_build_triggerurl(self):
#         self.assertEquals(
#             self.j.get_build_triggerurl(), 'http://halob:8080/job/foo/build')

#     def test_wrong__mk_json_from_build_parameters(self):
#         with self.assertRaises(AssertionError) as ar:
#             self.j._mk_json_from_build_parameters(build_params='bad parameter')

#         self.assertEquals(
#             ar.exception.message, 'Build parameters must be a dict')

#     def test__mk_json_from_build_parameters(self):
#         params = {'param1': 'value1', 'param2': 'value2'}
#         ret = self.j.mk_json_from_build_parameters(build_params=params)
#         self.assertTrue(isinstance(ret, str))
#         self.assertEquals(ret,
#                           '{"parameter": [{"name": "param2", "value": "value2"}, {"name": "param1", "value": "value1"}]}')

#     def test_wrong_mk_json_from_build_parameters(self):
#         with self.assertRaises(AssertionError) as ar:
#             self.j.mk_json_from_build_parameters(build_params='bad parameter')

#         self.assertEquals(
#             ar.exception.message, 'Build parameters must be a dict')

#     @mock.patch.object(JenkinsBase, 'get_data', fakeGetData)
#     def test_wrong_field__build_id_for_type(self):
#         with self.assertRaises(AssertionError):
#             self.j._buildid_for_type('wrong')

#     @mock.patch.object(JenkinsBase, 'get_data', fakeGetData)
#     def test_get_last_good_buildnumber(self):
#         ret = self.j.get_last_good_buildnumber()
#         self.assertTrue(ret, 3)

#     @mock.patch.object(JenkinsBase, 'get_data', fakeGetData)
#     def test_get_last_failed_buildnumber(self):
#         with self.assertRaises(NoBuildData):
#             self.j.get_last_failed_buildnumber()

#     @mock.patch.object(JenkinsBase, 'get_data', fakeGetData)
#     def test_get_last_buildnumber(self):
#         ret = self.j.get_last_buildnumber()
#         self.assertEquals(ret, 3)

#     @mock.patch.object(JenkinsBase, 'get_data', fakeGetData)
#     def test_get_last_completed_buildnumber(self):
#         ret = self.j.get_last_completed_buildnumber()
#         self.assertEquals(ret, 3)

#     def test_get_build_dict(self):
#         ret = self.j.get_build_dict()
#         self.assertTrue(isinstance(ret, dict))
#         self.assertEquals(len(ret), 3)

#     @mock.patch.object(Job, '_poll')
#     def test_nobuilds_get_build_dict(self, _poll):
#         # Bare minimum build dict, we only testing dissapearance of 'builds'
#         _poll.return_value = {"name": "foo"}

#         j = Job('http://halob:8080/job/foo/', 'foo', self.J)
#         with self.assertRaises(NoBuildData):
#             j.get_build_dict()

#     def test_get_build_ids(self):
#         # We don't want to deal with listreverseiterator here
#         # So we convert result to a list
#         ret = list(self.j.get_build_ids())
#         self.assertTrue(isinstance(ret, list))
#         self.assertEquals(len(ret), 3)

#     @mock.patch.object(Job, '_poll')
#     def test_nobuilds_get_revision_dict(self, _poll):
#         # Bare minimum build dict, we only testing dissapearance of 'builds'
#         _poll.return_value = {"name": "foo"}

#         j = Job('http://halob:8080/job/foo/', 'foo', self.J)
#         with self.assertRaises(NoBuildData):
#             j.get_revision_dict()


# if __name__ == '__main__':
#     unittest.main()
