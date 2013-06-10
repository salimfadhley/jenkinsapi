import mock
import unittest
import datetime

from jenkinsapi.build import Build

class TestTimestamps(unittest.TestCase):

	DATA = { 'actions': [{'causes': [{'shortDescription': 'Started by user anonymous',
                          'userId': None,
                          'userName': 'anonymous'}]}],
			 'artifacts': [],
			 'building': False,
			 'builtOn': '',
			 'changeSet': {'items': [], 'kind': None},
			 'culprits': [],
			 'description': None,
			 'duration': 106,
			 'estimatedDuration': 106,
			 'executor': None,
			 'fullDisplayName': 'foo #1',
			 'id': '2013-05-31_23-15-40',
			 'keepLog': False,
			 'number': 1,
			 'result': 'SUCCESS',
			 'timestamp': 1370042140000,
			 'url': 'http://localhost:8080/job/foo/1/'}

	@mock.patch.object(Build, '_poll')
	def setUp(self, _poll):
		_poll.return_value = self.DATA
		self.j = mock.MagicMock() # Job
		self.j.name = 'FooJob'

		self.b = Build('http://', 97, self.j)

	def test_timestamp(self):
		self.assertIsInstance(self.b.get_timestamp(), datetime.datetime)
		self.assertEqual(self.b.get_timestamp(), datetime.datetime(2013, 5, 31, 23, 15, 40))

	def testName(self):
		with self.assertRaises(AttributeError):
			_ = self.b.id()
		self.assertEquals(self.b.name, 'foo #1')
