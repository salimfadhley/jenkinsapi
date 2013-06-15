import mock
import unittest
import datetime
import urllib2

from jenkinsapi.jenkins import Jenkins, JenkinsBase, View, Job
from jenkinsapi.utils.requester import Requester
from jenkinsapi.exceptions import UnknownJob, NotAuthorized, JenkinsAPIException


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

    @mock.patch.object(Jenkins, '_poll')
    def test_reload(self, _poll):
        mock_requester = Requester(username='foouser', password='foopassword')
        mock_requester.get_url = mock.MagicMock(return_value='')
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword', 
                    requester=mock_requester)
        J.reload()

    @mock.patch.object(Jenkins, '_poll')
    def test_unauthorised_reload(self, _poll):
        def fail_get_url(url):
            raise urllib2.HTTPError(url=url, code=403, 
                msg='You are not authorized to reload this server',
                hdrs=None, fp=None)

        _poll.return_value = {}
        mock_requester = Requester(username='foouser', password='foopassword')
        mock_requester.get_url = mock.MagicMock(return_value='', 
                side_effect=fail_get_url)
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword', 
                    requester=mock_requester)
        with self.assertRaises(NotAuthorized) as na:
            J.reload()

        self.assertEquals(na.exception.message, 
                'You are not authorized to reload this server')

    @mock.patch.object(Jenkins, '_poll')
    def test_httperror_reload(self, _poll):
        def fail_get_url(url):
            raise urllib2.HTTPError(url=url, code=500, 
                    msg='Because I said so!', hdrs=None, fp=None)

        _poll.return_value = {}
        mock_requester = Requester(username='foouser', password='foopassword')
        mock_requester.get_url = mock.MagicMock(return_value='', 
                side_effect=fail_get_url)
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword', 
                    requester=mock_requester)
        with self.assertRaises(urllib2.HTTPError) as ar:
            J.reload()
        http_error = ar.exception
        self.assertEquals(http_error.code, 500)

    @mock.patch.object(JenkinsBase, '_poll')
    @mock.patch.object(Jenkins, '_poll')
    @mock.patch.object(Job, '_poll')
    def test_get_jobs(self, _base_poll, _poll, _job_poll):
        _poll.return_value = {'jobs': [
                        {'name': 'job_one', 
                         'url': 'http://localhost:8080/job_one'},
                        {'name': 'job_two', 
                         'url': 'http://localhost:8080/job_two'},
                        ]}
        _base_poll.return_value = _poll.return_value
        _job_poll.return_value = {}
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword')
        for idx, (job_name, job) in enumerate(J.get_jobs()):
            self.assertEquals(
                    job_name, _poll.return_value['jobs'][idx]['name']) 
            self.assertTrue(isinstance(job, Job))
            self.assertEquals(
                    job.name, _poll.return_value['jobs'][idx]['name'])
            self.assertEquals(
                    job.baseurl, _poll.return_value['jobs'][idx]['url'])

    @mock.patch.object(JenkinsBase, '_poll')
    @mock.patch.object(Jenkins, '_poll')
    @mock.patch.object(Job, '_poll')
    def test_get_jobs_info(self, _base_poll, _poll, _job_poll):
        _poll.return_value = {'jobs': [
                        {'name': 'job_one', 
                         'url': 'http://localhost:8080/job_one'},
                        {'name': 'job_two', 
                         'url': 'http://localhost:8080/job_two'},
                        ]}
        _base_poll.return_value = _poll.return_value
        _job_poll.return_value = {}
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword')
        for idx, (url, job_name) in enumerate(J.get_jobs_info()):
            self.assertEquals(
                    job_name, _poll.return_value['jobs'][idx]['name']) 
            self.assertEquals(
                    url, _poll.return_value['jobs'][idx]['url'])

    @mock.patch.object(JenkinsBase, '_poll')
    @mock.patch.object(Jenkins, '_poll')
    @mock.patch.object(Job, '_poll')
    def test_get_jobs_list(self, _base_poll, _poll, _job_poll):
        _poll.return_value = {'jobs': [
                        {'name': 'job_one', 
                         'url': 'http://localhost:8080/job_one'},
                        {'name': 'job_two', 
                         'url': 'http://localhost:8080/job_two'},
                        ]}
        _base_poll.return_value = _poll.return_value
        _job_poll.return_value = {}
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword')
        for idx, job_name in enumerate(J.get_jobs_list()):
            self.assertEquals(
                    job_name, _poll.return_value['jobs'][idx]['name']) 

    @mock.patch.object(JenkinsBase, '_poll')
    @mock.patch.object(Jenkins, '_poll')
    @mock.patch.object(Job, '_poll')
    def test_get_job(self, _base_poll, _poll, _job_poll):
        _poll.return_value = {'jobs': [
                        {'name': 'job_one', 
                         'url': 'http://localhost:8080/job_one'},
                        {'name': 'job_two', 
                         'url': 'http://localhost:8080/job_two'},
                        ]}
        _base_poll.return_value = _poll.return_value
        _job_poll.return_value = {}
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword')
        job = J.get_job('job_one')
        self.assertTrue(isinstance(job, Job))
        self.assertEquals(
                job.name, _poll.return_value['jobs'][0]['name'])
        self.assertEquals(
                job.baseurl, _poll.return_value['jobs'][0]['url'])

    @mock.patch.object(JenkinsBase, '_poll')
    @mock.patch.object(Jenkins, '_poll')
    @mock.patch.object(Job, '_poll')
    def test_has_job(self, _base_poll, _poll, _job_poll):
        _poll.return_value = {'jobs': [
                        {'name': 'job_one', 
                         'url': 'http://localhost:8080/job_one'},
                        {'name': 'job_two', 
                         'url': 'http://localhost:8080/job_two'},
                        ]}
        _base_poll.return_value = _poll.return_value
        _job_poll.return_value = {}
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword')
        job = J.has_job('job_one')
        self.assertTrue(job)

    @mock.patch.object(JenkinsBase, '_poll')
    @mock.patch.object(Jenkins, '_poll')
    @mock.patch.object(Job, '_poll')
    def test_has_no_job(self, _base_poll, _poll, _job_poll):
        _poll.return_value = {'jobs': [
                        {'name': 'job_one', 
                         'url': 'http://localhost:8080/job_one'},
                        {'name': 'job_two', 
                         'url': 'http://localhost:8080/job_two'},
                        ]}
        _base_poll.return_value = _poll.return_value
        _job_poll.return_value = {}
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword')
        job = J.has_job('inexistant_job')
        self.assertFalse(job)

    @mock.patch.object(JenkinsBase, '_poll')
    @mock.patch.object(Jenkins, '_poll')
    @mock.patch.object(Job, '_poll')
    def test_create_dup_job(self, _base_poll, _poll, _job_poll):
        _poll.return_value = {'jobs': [
                        {'name': 'job_one', 
                         'url': 'http://localhost:8080/job_one'},
                        {'name': 'job_two', 
                         'url': 'http://localhost:8080/job_two'},
                        ]}
        _base_poll.return_value = _poll.return_value
        _job_poll.return_value = {}
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword')
        job = J.create_job('job_one', None)
        self.assertTrue(isinstance(job, Job))
        self.assertTrue(job.baseurl=='http://localhost:8080/job_one')
        self.assertTrue(job.name=='job_one')

    # Here we're going to test function, which is going to modify
    # Jenkins internal data. It calls for data once to check 
    # if job already there, then calls again to see if job hs been created.
    # So we need to create mock function, which
    # will return different value per each call

    # Define what we will return
    create_job_returns = [
            # This will be returned when job is not yet created
                {'jobs': [
                        {'name': 'job_one', 
                         'url': 'http://localhost:8080/job_one'},
                        {'name': 'job_one', 
                         'url': 'http://localhost:8080/job_one'},
                        ]},
            # This to simulate that the job has been created
              {'jobs': [
                        {'name': 'job_one', 
                         'url': 'http://localhost:8080/job_one'},
                        {'name': 'job_two', 
                         'url': 'http://localhost:8080/job_two'},
                        {'name': 'job_new', 
                         'url': 'http://localhost:8080/job_new'},
                        ]}
              ]

    # Mock function
    def second_call_poll():
        return TestJenkins.create_job_returns.pop(0)

    # Patch Jenkins with mock function
    @mock.patch.object(Jenkins, '_poll', side_effect=second_call_poll)
    @mock.patch.object(Job, '_poll')
    def test_create_new_job(self, _poll, _job_poll):
        _job_poll.return_value = {}

        mock_requester = Requester(username='foouser', password='foopassword')
        mock_requester.post_xml_and_confirm_status = mock.MagicMock(
                return_value='')

        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword',
                    requester=mock_requester)

        job = J.create_job('job_new', None)
        self.assertTrue(isinstance(job, Job))
        self.assertTrue(job.baseurl=='http://localhost:8080/job_new')
        self.assertTrue(job.name=='job_new')

    @mock.patch.object(JenkinsBase, '_poll')
    @mock.patch.object(Jenkins, '_poll')
    @mock.patch.object(Job, '_poll')
    def test_create_new_job_fail(self, _base_poll, _poll, _job_poll):
        _job_poll.return_value = {}
        _poll.return_value = {'jobs': [
                        {'name': 'job_one', 
                         'url': 'http://localhost:8080/job_one'},
                        {'name': 'job_one', 
                         'url': 'http://localhost:8080/job_one'},
                        ]}
        _base_poll.return_value = _poll.return_value

        mock_requester = Requester(username='foouser', password='foopassword')
        mock_requester.post_xml_and_confirm_status = mock.MagicMock(
                return_value='')

        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword',
                    requester=mock_requester)

        with self.assertRaises(JenkinsAPIException) as ar:
            job = J.create_job('job_new', None)

        self.assertEquals(ar.exception.message, 'Cannot create job job_new')

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

    @mock.patch.object(Jenkins, '_poll')
    def test_get_base_server_url(self, _poll):
        _poll.return_value = {}
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword')
        self.assertEquals(J.baseurl, 'http://localhost:8080')
        self.assertEquals(
            J.get_base_server_url(), 'http://localhost:8080')
        
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
