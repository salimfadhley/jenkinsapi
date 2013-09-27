import mock
import unittest

from collections import defaultdict
from jenkinsapi import config
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.queue import Queue, QueueItem
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.job import Job

class FourOhFourError(Exception):
    """
    Missing fake data
    """

class TestQueue(unittest.TestCase):

    @classmethod
    def mockGetData(self, url):
        try:
            return TestQueue.URL_DATA[url]
        except KeyError:
            raise FourOhFourError(url)

    URL_DATA = {}

    URL_DATA['http://localhost:8080/%s' % config.JENKINS_API] = \
        {'jobs':[
            {'name':'utmebvpxrw', 
              'url':'http://localhost/job/utmebvpxrw'}
              ]
        }

    URL_DATA['http://localhost/job/utmebvpxrw/%s' % config.JENKINS_API] = \
        {}


    URL_DATA['http://localhost:8080/queue/%s' % config.JENKINS_API] = \
        {'items': [{'actions': [{'causes': [{'shortDescription': 'Started by user anonymous',
                                     'userId': None,
                                     'userName': 'anonymous'}]}],
            'blocked': False,
            'buildable': True,
            'buildableStartMilliseconds': 1371419916747,
            'id': 42,
            'inQueueSince': 1371419909428,
            'params': '',
            'stuck': False,
            'task': {'color': 'grey',
                     'name': 'klscuimkqo',
                     'url': 'http://localhost:8080/job/klscuimkqo/'},
            'why': 'Waiting for next available executor'},
           {'actions': [{'causes': [{'shortDescription': 'Started by user anonymous',
                                     'userId': None,
                                     'userName': 'anonymous'}]}],
            'blocked': False,
            'buildable': True,
            'buildableStartMilliseconds': 1371419911747,
            'id': 41,
            'inQueueSince': 1371419906327,
            'params': '',
            'stuck': False,
            'task': {'color': 'grey',
                     'name': 'vluyhzzepl',
                     'url': 'http://localhost:8080/job/vluyhzzepl/'},
            'why': 'Waiting for next available executor'},
           {'actions': [{'causes': [{'shortDescription': 'Started by user anonymous',
                                     'userId': None,
                                     'userName': 'anonymous'}]}],
            'blocked': False,
            'buildable': True,
            'buildableStartMilliseconds': 1371419911747,
            'id': 40,
            'inQueueSince': 1371419903212,
            'params': '',
            'stuck': False,
            'task': {'color': 'grey',
                     'name': 'utmebvpxrw',
                     'url': 'http://localhost:8080/job/utmebvpxrw/'},
            'why': 'Waiting for next available executor'}]}


    @mock.patch.object(JenkinsBase, 'get_data', mockGetData)
    def setUp(self):
        self.J = Jenkins('http://localhost:8080')  # Jenkins
        self.q = Queue('http://localhost:8080/queue', self.J)

    def testRepr(self):
        self.assertTrue(repr(self.q))

    def test_length(self):
        self.assertEquals(len(self.q), 3)

    def test_list_items(self):
        self.assertEquals(set(self.q.keys()), set([40,41,42]))

    def test_getitem(self):
        item40 = self.q[40]
        self.assertIsInstance(item40, QueueItem)

    @mock.patch.object(JenkinsBase, 'get_data', mockGetData)
    def test_get_job_for_queue_item(self):
        item40 = self.q[40]
        j = item40.get_job()
        self.assertIsInstance(j, Job)

if __name__ == '__main__':
    unittest.main()
