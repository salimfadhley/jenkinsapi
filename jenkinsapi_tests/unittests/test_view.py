import mock
import unittest

from jenkinsapi.view import View

class TestView(unittest.TestCase):

    DATA = {'description': 'Important Shizz',
            'jobs': [{'color': 'blue',
                      'name': 'foo',
                      'url': 'http://halob:8080/job/foo/'},
           {'color': 'red',
            'name': 'test_jenkinsapi',
            'url': 'http://halob:8080/job/test_jenkinsapi/'}],
            'name': 'FodFanFo',
            'property': [],
            'url': 'http://halob:8080/view/FodFanFo/'}

    @mock.patch.object(View, '_poll')
    def setUp(self, _poll):
        _poll.return_value = self.DATA

        # def __init__(self, url, name, jenkins_obj)
        self.J = mock.MagicMock()  # Jenkins object
        self.v = View('http://localhost:800/view/FodFanFo', 'FodFanFo', self.J)

    def testRepr(self):
        # Can we produce a repr string for this object
        repr(self.v)

    def testName(self):
        with self.assertRaises(AttributeError):
            self.v.id()
        self.assertEquals(self.v.name, 'FodFanFo')

if __name__ == '__main__':
    unittest.main()
