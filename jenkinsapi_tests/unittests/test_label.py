#import mock
#import unittest
#
#from jenkinsapi.label import Label
#from jenkinsapi.node import Node
#from jenkinsapi.job import Job
#
#
#class TestLabel(unittest.TestCase):
#    LABEL = {"actions": [],
#             "busyExecutors": 0,
#             "clouds": [],
#             "description": "A Label",
#             "idleExecutors": 0,
#             "loadStatistics": {},
#             "name": "label_testLabel",
#             "nodes": [{"nodeName": "thenodeknows"}],
#             "offline": True,
#             "tiedJobs": [{"name": "testjob",
#                           "url": "http://",
#                           "color": "disabled"}],
#             "totalExecutors": 0,
#             "propertiesList": []}
#
#    @mock.patch.object(Label, "_poll")
#    def setUp(self, label_poll):
#        label_poll.return_value = self.LABEL
#
#        self.J = mock.MagicMock()
#        self.l = Label('label_testLabel', self.J)
#
#    def testRepr(self):
#        self.assertEqual(repr(self.l), '<jenkinsapi.label.Label label_testLabel>')
#
#    def testName(self):
#        self.assertEqual(self.l.name, "label_testLabel")
#
#    def testDescription(self):
#        self.assertEqual(self.l.description, "A Label")
#
#    def testJobs(self):
#        jobs = self.l.jobs
#        self.assertEqual(len(jobs), 1)
#        self.assertEqual(jobs[0], "testjob")
#
#    def testNodes(self):
#        nodes = self.l.nodes
#        self.assertEqual(len(nodes), 1)
#        self.assertEqual(nodes[0], "thenodeknows")
#
#
#if __name__ == '__main__':
#    unittest.main()
