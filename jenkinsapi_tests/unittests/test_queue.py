import mock
# To run unittests on python 2.6 please use unittest2 library
try:
    import unittest2 as unittest
except ImportError:
    import unittest

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
    QUEUE_DATA = {
        'items': [
            {
                'actions': [
                    {
                        'causes': [
                            {
                                'shortDescription': 'Started by user anonymous',
                                'userId': None,
                                'userName': 'anonymous'
                            }
                        ],
                        'parameters':
                        [{'name': 'name1', 'value': 'value1'},
                         {'name': 'node'}]
                    }
                ],
                'blocked': False,
                'buildable': True,
                'buildableStartMilliseconds': 1371419916747,
                'id': 42,
                'inQueueSince': 1371419909428,
                'params': '',
                'stuck': False,
                'task': {
                    'color': 'grey',
                    'name': 'klscuimkqo',
                    'url': 'http://localhost:8080/job/klscuimkqo/'
                },
                'why': 'Waiting for next available executor'
            },
            {
                'actions': [
                    {
                        'causes': [
                            {
                                'shortDescription': 'Started by user anonymous',
                                'userId': None,
                                'userName': 'anonymous'
                            }
                        ]
                    }
                ],
                'blocked': False,
                'buildable': True,
                'buildableStartMilliseconds': 1371419911747,
                'id': 41,
                'inQueueSince': 1371419906327,
                'params': '',
                'stuck': False,
                'task': {
                    'color': 'grey',
                    'name': 'vluyhzzepl',
                    'url': 'http://localhost:8080/job/vluyhzzepl/'
                },
                'why': 'Waiting for next available executor'
            },
            {
                'actions': [
                    {
                        'causes': [
                            {
                                'shortDescription': 'Started by user anonymous',
                                'userId': None,
                                'userName': 'anonymous'
                            }
                        ]
                    }
                ],
                'blocked': False,
                'buildable': True,
                'buildableStartMilliseconds': 1371419911747,
                'id': 40,
                'inQueueSince': 1371419903212,
                'params': '',
                'stuck': False,
                'task': {
                    'color': 'grey',
                    'name': 'utmebvpxrw',
                    'url': 'http://localhost:8080/job/utmebvpxrw/'
                },
                'why': 'Waiting for next available executor'
            }
        ]
    }

    @classmethod
    def mockGetData(self, url, tree):
        try:
            return TestQueue.URL_DATA[url]
        except KeyError:
            raise FourOhFourError(url)

    URL_DATA = {}

    URL_DATA['http://localhost:8080/%s' % config.JENKINS_API] = {
        'jobs': [
            {
                'name': 'utmebvpxrw',
                'color': 'blue',
                'url': 'http://localhost/job/utmebvpxrw'
            }
        ]
    }

    URL_DATA['http://localhost/job/utmebvpxrw/%s' % config.JENKINS_API] = {}

    URL_DATA['http://localhost:8080/queue/%s' %
             config.JENKINS_API] = QUEUE_DATA

    for item in QUEUE_DATA['items']:
        url = 'http://localhost:8080/queue/item/%i/%s' % (
            item['id'], config.JENKINS_API)
        print(url)
        URL_DATA[url] = item

    @mock.patch.object(JenkinsBase, 'get_data', mockGetData)
    def setUp(self):
        self.J = Jenkins('http://localhost:8080')  # Jenkins
        self.q = Queue('http://localhost:8080/queue', self.J)

    def testRepr(self):
        self.assertTrue(repr(self.q))

    def test_length(self):
        self.assertEquals(len(self.q), 3)

    def test_list_items(self):
        self.assertEquals(set(self.q.keys()), set([40, 41, 42]))

    @mock.patch.object(JenkinsBase, 'get_data', mockGetData)
    def test_getitem(self):
        item40 = self.q[40]
        self.assertIsInstance(item40, QueueItem)

    @mock.patch.object(JenkinsBase, 'get_data', mockGetData)
    def test_get_job_for_queue_item(self):
        item40 = self.q[40]
        j = item40.get_job()
        self.assertIsInstance(j, Job)

    @mock.patch.object(JenkinsBase, 'get_data', mockGetData)
    def test_get_queue_item_for_job(self):
        item40 = self.q.get_queue_items_for_job('klscuimkqo')
        self.assertIsInstance(item40, list)
        self.assertEquals(len(item40), 1)
        self.assertIsInstance(item40[0], QueueItem)


    @mock.patch.object(JenkinsBase, 'get_data', mockGetData)
    def test_qi_get_parameters(self):
        qi = self.q[42]
        self.assertEquals(qi.get_parameters(), {'name1': 'value1',
                                                'node': None})


if __name__ == '__main__':
    unittest.main()
