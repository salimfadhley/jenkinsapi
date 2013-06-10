import mock
import unittest
import datetime

from jenkinsapi.jenkins import Jenkins, JenkinsBase, View
from jenkinsapi.utils.requester import Requester


class TestJenkins(unittest.TestCase):

    DATA = {}

    @mock.patch.object(Jenkins, '_poll')
    def setUp(self, _poll):
        _poll.return_value = self.DATA
        self.J = Jenkins('http://localhost:8080',
                         username='foouser', password='foopassword')

    @mock.patch.object(Jenkins, '_poll')
    def test_clone(self, _poll):
        _poll.return_value = self.DATA
        JJ = self.J._clone()
        self.assertNotEquals(id(JJ), id(self.J))
        self.assertEquals(JJ, self.J)

    def test_stored_passwords(self):
        self.assertEquals(self.J.requester.password, 'foopassword')
        self.assertEquals(self.J.requester.username, 'foouser')


class TestJenkinsURLs(unittest.TestCase):

    @mock.patch.object(Jenkins, '_poll')
    def testNoSlash(self, _poll):
        _poll.return_value = {}
        J = Jenkins('http://localhost:8080',
                    username='foouser', password='foopassword')
        self.assertEquals(
            J.get_create_url(), 'http://localhost:8080/createItem')

    @mock.patch.object(Jenkins, '_poll')
    def testWithSlash(self, _poll):
        _poll.return_value = {}
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword')
        self.assertEquals(
            J.get_create_url(), 'http://localhost:8080/createItem')

        
class TestJenkinsViews(unittest.TestCase):

    @mock.patch.object(Jenkins, '_poll')
    @mock.patch.object(JenkinsBase, '_poll')
    def test_create_view(self, _poll, _base_poll):
        mock_requester = Requester(username='foouser', password='foopassword')
        mock_requester.get_url = mock.MagicMock(return_value='<div/>')
        mock_requester.post_url = mock.MagicMock(return_value='')
        _poll.return_value = {'views': [
                        {'name': 'All', 
                         'url': 'http://localhost:8080/views/All'},
                        {'name': 'NewView', 
                         'url': 'http://localhost:8080/views/NewView'},
                        ]}
        _base_poll.return_value = _poll.return_value
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword', 
                    requester=mock_requester)
        new_view = J.create_view(str_view_name='NewView', person=None)
        self.assertTrue(isinstance(new_view, View))
        self.assertEquals(new_view.baseurl, 
                'http://localhost:8080/views/NewView')

    @mock.patch.object(Jenkins, '_poll')
    def test_create_existing_view(self, _poll):
        mock_requester = Requester(username='foouser', password='foopassword')
        mock_requester.get_url = mock.MagicMock(
                return_value='A view already exists')
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword', 
                    requester=mock_requester)
        new_view = J.create_view(str_view_name='NewView', person=None)
        self.assertFalse(isinstance(new_view, View))

    @mock.patch.object(Jenkins, '_poll')
    def test_delete_inexisting_view(self, _poll):
        mock_requester = Requester(username='foouser', password='foopassword')
        mock_requester.get_url = mock.MagicMock(return_value='<div/>')
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword', 
                    requester=mock_requester)
        delete_result = J.delete_view(str_view_name='NewView', person=None)
        self.assertFalse(delete_result)

    @mock.patch.object(Jenkins, '_poll')
    def test_delete_existing_view(self, _poll):
        mock_requester = Requester(username='foouser', password='foopassword')
        mock_requester.get_url = mock.MagicMock(return_value='View exists')
        _poll.return_value = {'views': [
                        {'name': 'All', 
                         'url': 'http://localhost:8080/views/All'},
                        ]}
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword', 
                    requester=mock_requester)
        delete_result = J.delete_view(str_view_name='NewView', person=None)
        self.assertTrue(delete_result)


if __name__ == '__main__':
    unittest.main()
