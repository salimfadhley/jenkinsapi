import mock
# To run unittests on python 2.6 please use unittest2 library
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from jenkinsapi.plugins import Plugins
from jenkinsapi.utils.requester import Requester
from jenkinsapi.jenkins import Jenkins, JenkinsBase, Job
from jenkinsapi.custom_exceptions import JenkinsAPIException


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
        J.poll()

    @mock.patch.object(JenkinsBase, '_poll')
    @mock.patch.object(Jenkins, '_poll')
    @mock.patch.object(Job, '_poll')
    def test_lazy_loading(self, _base_poll, _poll, _job_poll):
        _poll.return_value = {
            'jobs': [
                {'name': 'job_one',
                 'url': 'http://localhost:8080/job_one',
                 'color': 'blue'},
                {'name': 'job_two',
                 'url': 'http://localhost:8080/job_two',
                 'color': 'blue'},
            ]
        }
        _base_poll.return_value = _poll.return_value
        _job_poll.return_value = {}
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword', lazy=True)

        self.assertEquals(J._data, None)

        for idx, (job_name, job) in enumerate(J.get_jobs()):
            self.assertEquals(
                job_name,
                _poll.return_value['jobs'][idx]['name'])
            self.assertTrue(isinstance(job, Job))
            self.assertEquals(
                job.name,
                _poll.return_value['jobs'][idx]['name'])
            self.assertEquals(
                job.baseurl,
                _poll.return_value['jobs'][idx]['url'])

    @mock.patch.object(JenkinsBase, '_poll')
    @mock.patch.object(Jenkins, '_poll')
    @mock.patch.object(Job, '_poll')
    def test_get_jobs_info(self, _base_poll, _poll, _job_poll):
        _poll.return_value = {
            'jobs': [
                {'name': 'job_one',
                 'url': 'http://localhost:8080/job_one',
                 'color': 'blue'},
                {'name': 'job_two',
                 'url': 'http://localhost:8080/job_two',
                 'color': 'blue'},
            ]
        }
        _base_poll.return_value = _poll.return_value
        _job_poll.return_value = {}
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword')
        for idx, (url, job_name) in enumerate(J.get_jobs_info()):
            self.assertEquals(
                job_name,
                _poll.return_value['jobs'][idx]['name'])
            self.assertEquals(url, _poll.return_value['jobs'][idx]['url'])

    @mock.patch.object(JenkinsBase, '_poll')
    @mock.patch.object(Jenkins, '_poll')
    @mock.patch.object(Job, '_poll')
    def test_get_jobs_list(self, _base_poll, _poll, _job_poll):
        _poll.return_value = {
            'jobs': [
                {'name': 'job_one',
                 'url': 'http://localhost:8080/job_one',
                 'color': 'blue'},
                {'name': 'job_two',
                 'url': 'http://localhost:8080/job_two',
                 'color': 'blue'},
            ]
        }
        _base_poll.return_value = _poll.return_value
        _job_poll.return_value = {}
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword')
        for idx, job_name in enumerate(J.get_jobs_list()):
            self.assertEquals(
                job_name,
                _poll.return_value['jobs'][idx]['name'])

    @mock.patch.object(JenkinsBase, '_poll')
    @mock.patch.object(Jenkins, '_poll')
    @mock.patch.object(Job, '_poll')
    def test_create_dup_job(self, _base_poll, _poll, _job_poll):
        _poll.return_value = {
            'jobs': [
                {'name': 'job_one',
                 'url': 'http://localhost:8080/job/job_one',
                 'color': 'blue'},
                {'name': 'job_two',
                 'url': 'http://localhost:8080/job/job_two',
                 'color': 'blue'},
            ]
        }
        _base_poll.return_value = _poll.return_value
        _job_poll.return_value = {}
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword')
        job = J.create_job('job_one', None)
        self.assertTrue(isinstance(job, Job))
        self.assertTrue(job.baseurl == 'http://localhost:8080/job/job_one')
        self.assertTrue(job.name == 'job_one')

    # Here we're going to test function, which is going to modify
    # Jenkins internal data. It calls for data once to check
    # if job already there, then calls again to see if job hs been created.
    # So we need to create mock function, which
    # will return different value per each call

    # Define what we will return
    create_job_returns = [
        # This will be returned when job is not yet created
        {
            'jobs': [
                {'name': 'job_one',
                 'url': 'http://localhost:8081/job_one',
                 'color': 'blue'},
                {'name': 'job_one',
                 'url': 'http://localhost:8080/job_one',
                 'color': 'blue'},
            ]
        },
        # This to simulate that the job has been created
        {
            'jobs': [
                {'name': 'job_one',
                 'url': 'http://localhost:8080/job_one',
                 'color': 'blue'},
                {'name': 'job_two',
                 'url': 'http://localhost:8080/job_two',
                 'color': 'blue'},
                {'name': 'job_new',
                 'url': 'http://localhost:8080/job_new',
                 'color': 'blue'},
            ]
        }
    ]

    @mock.patch.object(JenkinsBase, '_poll')
    @mock.patch.object(Jenkins, '_poll')
    @mock.patch.object(Job, '_poll')
    def test_create_new_job_fail(self, _base_poll, _poll, _job_poll):
        _job_poll.return_value = {}
        _poll.return_value = {
            'jobs': [
                {'name': 'job_one',
                 'url': 'http://localhost:8080/job_one',
                 'color': 'blue'},
                {'name': 'job_one',
                 'url': 'http://localhost:8080/job_one',
                 'color': 'blue'},
            ]
        }
        _base_poll.return_value = _poll.return_value

        mock_requester = Requester(username='foouser', password='foopassword')
        mock_requester.post_xml_and_confirm_status = mock.MagicMock(
            return_value='')

        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword',
                    requester=mock_requester)

        with self.assertRaises(JenkinsAPIException) as ar:
            J.create_job('job_new', None)

        self.assertEquals(str(ar.exception), 'Job XML config cannot be empty')

    @mock.patch.object(JenkinsBase, '_poll')
    @mock.patch.object(Jenkins, '_poll')
    @mock.patch.object(Job, '_poll')
    def test_get_jenkins_obj_from_url(self, _base_poll, _poll, _job_poll):
        _job_poll.return_value = {}
        _poll.return_value = {
            'jobs': [
                {'name': 'job_one',
                 'url': 'http://localhost:8080/job_one',
                 'color': 'blue'},
                {'name': 'job_one',
                 'url': 'http://localhost:8080/job_one',
                 'color': 'blue'},
            ]
        }
        _base_poll.return_value = _poll.return_value

        mock_requester = Requester(username='foouser', password='foopassword')
        mock_requester.post_xml_and_confirm_status = mock.MagicMock(
            return_value='')

        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword',
                    requester=mock_requester)

        new_jenkins = J.get_jenkins_obj_from_url('http://localhost:8080/')
        self.assertEquals(new_jenkins, J)

        new_jenkins = J.get_jenkins_obj_from_url('http://localhost:8080/foo')
        self.assertNotEquals(new_jenkins, J)

    @mock.patch.object(JenkinsBase, '_poll')
    @mock.patch.object(Jenkins, '_poll')
    @mock.patch.object(Job, '_poll')
    def test_get_jenkins_obj(self, _base_poll, _poll, _job_poll):
        _job_poll.return_value = {}
        _poll.return_value = {
            'jobs': [
                {'name': 'job_one',
                 'url': 'http://localhost:8080/job_one',
                 'color': 'blue'},
                {'name': 'job_one',
                 'url': 'http://localhost:8080/job_one',
                 'color': 'blue'},
            ]
        }
        _base_poll.return_value = _poll.return_value

        mock_requester = Requester(username='foouser', password='foopassword')
        mock_requester.post_xml_and_confirm_status = mock.MagicMock(
            return_value='')

        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword',
                    requester=mock_requester)

        new_jenkins = J.get_jenkins_obj()
        self.assertEquals(new_jenkins, J)

    @mock.patch.object(JenkinsBase, '_poll')
    @mock.patch.object(Jenkins, '_poll')
    def test_get_version(self, _base_poll, _poll):
        class MockResponse(object):

            def __init__(self):
                self.headers = {}
                self.headers['X-Jenkins'] = '1.542'
        mock_requester = Requester(username='foouser', password='foopassword')
        mock_requester.get_and_confirm_status = mock.MagicMock(
            return_value=MockResponse())
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword',
                    requester=mock_requester)
        self.assertEquals('1.542', J.version)

    @mock.patch.object(JenkinsBase, '_poll')
    @mock.patch.object(Jenkins, '_poll')
    def test_get_version_nonexistent(self, _base_poll, _poll):
        class MockResponse(object):

            def __init__(self):
                self.headers = {}
        base_url = 'http://localhost:8080'
        mock_requester = Requester(username='foouser', password='foopassword')
        mock_requester.get_and_confirm_status = mock.MagicMock(
            return_value=MockResponse())
        J = Jenkins(base_url,
                    username='foouser', password='foopassword',
                    requester=mock_requester)
        self.assertEquals('0.0', J.version)

    @mock.patch.object(JenkinsBase, 'get_data')
    def test_get_master_data(self, _base_poll):
        base_url = 'http://localhost:808'
        _base_poll.return_value = {
            "busyExecutors": 59,
            "totalExecutors": 75
        }
        j = Jenkins(base_url,
                    username='foouser', password='foopassword')
        data = j.get_master_data()
        self.assertEquals(data['busyExecutors'], 59)
        self.assertEquals(data['totalExecutors'], 75)


class TestJenkinsURLs(unittest.TestCase):

    @mock.patch.object(Jenkins, '_poll')
    def testNoSlash(self, _poll):
        _poll.return_value = {}
        J = Jenkins('http://localhost:8080',
                    username='foouser', password='foopassword')
        self.assertEquals(
            J.get_create_url(),
            'http://localhost:8080/createItem')

    @mock.patch.object(Jenkins, '_poll')
    def testWithSlash(self, _poll):
        _poll.return_value = {}
        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword')
        self.assertEquals(
            J.get_create_url(),
            'http://localhost:8080/createItem')

    @mock.patch.object(Jenkins, '_poll')
    @mock.patch.object(Plugins, '_poll')
    def test_has_plugin(self, _p_poll, _poll):
        _poll.return_value = {}
        _p_poll.return_value = {
            'plugins': [
                {
                    'deleted': False, 'hasUpdate': True, 'downgradable': False,
                    'dependencies': [{}, {}, {}, {}],
                    'longName': 'Jenkins Subversion Plug-in', 'active': True,
                    'shortName': 'subversion', 'backupVersion': None,
                    'url': 'http://wiki.jenkins-ci.org/'
                    'display/JENKINS/Subversion+Plugin',
                    'enabled': True, 'pinned': False, 'version': '1.45',
                    'supportsDynamicLoad': 'MAYBE', 'bundled': True
                }
            ]
        }

        J = Jenkins('http://localhost:8080/',
                    username='foouser', password='foopassword')
        self.assertTrue(J.has_plugin('subversion'))

if __name__ == '__main__':
    unittest.main()
