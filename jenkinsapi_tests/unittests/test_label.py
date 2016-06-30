import mock
# To run unittests on python 2.6 please use unittest2 library
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from jenkinsapi.label import Label


class TestLabel(unittest.TestCase):

    DATA = {"actions":[],
             "busyExecutors":0,
             "clouds":[],
             "description":None,
             "idleExecutors":0,
             "loadStatistics":{},
             "name":"jenkins-slave",
             "nodes":[],
             "offline":True,
             "tiedJobs":[
                    {"name":"test_job1",
                    "url":"http://jtest:8080/job/test_job1/",
                    "color":"blue"},
                    {"name":"test_job2",
                    "url":"http://jtest:8080/job/test_job2/",
                    "color":"blue"},
                    {"name":"test_job3",
                    "url":"http://jtest:8080/job/test_job3/",
                    "color":"blue"},
                    {"name":"test_job4",
                    "url":"http://jtest:8080/job/test_job4/",
                    "color":"blue"}],
              "totalExecutors":0,
              "propertiesList":[]}

    DATA_JOB_NAMES = {"tiedJobs":
                  [{"name":"test_job1"},
                   {"name":"test_job2"},
                   {"name":"test_job3"},
                   {"name":"test_job4"}]}

    DATA_JOBS = [{"url":"http://jtest:8080/job/test_job1/",
            "color":"blue",
            "name":"test_job1"},
           {"url":"http://jtest:8080/job/test_job2/",
            "color":"blue",
            "name":"test_job2"},
           {"url":"http://jtest:8080/job/test_job3/",
            "color":"blue",
            "name":"test_job3"},
           {"url":"http://jtest:8080/job/test_job4/",
            "color":"blue",
            "name":"test_job4"}]

    @mock.patch.object(Label, '_poll')
    def setUp(self, _poll):
        _poll.return_value = self.DATA

        # def __init__(self, baseurl, labelname, jenkins_obj):

        self.J = mock.MagicMock()  # Jenkins object
        self.n = Label('http://jtest:8080', 'jenkins-slave', self.J)

    def testRepr(self):
        # Can we produce a repr string for this object
        repr(self.n)

    def testName(self):
        with self.assertRaises(AttributeError):
            self.n.id()
        self.assertEquals(self.n.labelname, 'jenkins-slave')

    @mock.patch.object(Label, '_poll')
    def test_get_tied_job_names(self, _poll):
        _poll.return_value = self.DATA
        return self.assertEquals(self.n.get_tied_job_names(), self.DATA_JOBS)

    @mock.patch.object(Label, '_poll')
    def test_online(self, _poll):
        _poll.return_value = self.DATA
        return self.assertEquals(self.n.is_online(), False)

if __name__ == '__main__':
    unittest.main()
