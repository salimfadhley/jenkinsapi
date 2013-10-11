import mock
import unittest
from jenkinsapi import config
from jenkinsapi.view import View
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.utils.requester import Requester


class TestDataMissing(Exception):
    pass


class TestViews(unittest.TestCase):
    @mock.patch.object(Jenkins, '_poll')
    @mock.patch.object(JenkinsBase, '_poll')
    def test_create_view(self, _poll, _base_poll):
        mock_requester = Requester(username='foouser', password='foopassword')
        mock_requester.get_url = mock.MagicMock(return_value='<div/>')
        mock_requester.post_url = mock.MagicMock(return_value='')
        _poll.return_value = {
            'views': [
                {'name': 'All', 'url': 'http://localhost:8080/views/All'},
                {'name': 'NewView', 'url': 'http://localhost:8080/views/NewView'},
            ]
        }
        _base_poll.return_value = _poll.return_value
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword',
                    requester=mock_requester)

        new_view = J.views.create('NewView')
        self.assertTrue(isinstance(new_view, View))
        self.assertEquals(new_view.baseurl,
                          'http://localhost:8080/views/NewView')

    def test_create_existing_view(self):
        """
        Assert that attempting to create a view which
        already exists simply returns the same view.
        """
        def mockGetData(JJ, url):
            DATA = {}
            DATA['http://localhost:8080/%s' % config.JENKINS_API] = \
                {'views': [dict(name='NewView', url='http://xxxxx/yyyy')]}
            DATA['http://xxxxx/yyyy/%s' % config.JENKINS_API] = \
                {}

            try:
                result = DATA[url]

                return result
            except KeyError:
                raise TestDataMissing(url)

        with mock.patch.object(JenkinsBase, 'get_data', mockGetData):

            J = Jenkins('http://localhost:8080', username='foouser', password='foopassword')

            new_view = J.views.create('NewView')

            self.assertIsInstance(new_view, View)

    # @mock.patch.object(Jenkins, '_poll')
    # def test_delete_inexisting_view(self, _poll):
    #     mock_requester = Requester(username='foouser', password='foopassword')
    #     mock_requester.get_url = mock.MagicMock(return_value='<div/>')
    #     J = Jenkins('http://localhost:8080/',
    #                 username='foouser', password='foopassword',
    #                 requester=mock_requester)
    #     delete_result = J.delete_view(str_view_name='NewView')
    #     self.assertFalse(delete_result)

if __name__ == '__main__':
    unittest.main()
