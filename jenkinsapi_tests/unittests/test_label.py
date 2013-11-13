import mock
import unittest

from jenkinsapi.label import Label
from jenkinsapi.node import Node
from jenkinsapi.job import Job


class TestLabel(unittest.TestCase):
    LABEL = {"actions": [],
             "busyExecutors": 0,
             "clouds": [],
             "description": "A Label",
             "idleExecutors": 0,
             "loadStatistics": {},
             "name": "label_testLabel",
             "nodes": [{"nodeName": "thenodeknows"}],
             "offline": True,
             "tiedJobs": [{"name": "testjob",
                           "url": "http://",
                           "color": "disabled"}],
             "totalExecutors": 0,
             "propertiesList": []}

    JOB = {"actions": [],
           "description": "",
           "displayName": "testjob",
           "displayNameOrNull": None,
           "name": "testjob",
           "url": "http://",
           "buildable": True,
           "builds": [],
           "color": "grey",
           "firstBuild": None,
           "healthReport": [],
           "inQueue": False,
           "keepDependencies": False,
           "lastBuild": None,
           "lastCompletedBuild": None,
           "lastFailedBuild": None,
           "lastStableBuild": None,
           "lastSuccessfulBuild": None,
           "lastUnstableBuild": None,
           "lastUnsuccessfulBuild": None,
           "nextBuildNumber": 1,
           "property": [],
           "queueItem": None,
           "concurrentBuild": False,
           "downstreamProjects": [],
           "scm": {},
           "upstreamProjects": []}

    NODE = {"actions": [],
            "displayName": "thenodeknows",
            "executors": [{}],
            "icon": "computer.png",
            "idle": True,
            "jnlpAgent": False,
            "launchSupported": True,
            "loadStatistics": {},
            "manualLaunchAllowed": True,
            "monitorData": {"hudson.node_monitors.SwapSpaceMonitor": {"availablePhysicalMemory": 7681417216,
                                                                      "availableSwapSpace": 12195983360,
                                                                      "totalPhysicalMemory": 8374497280,
                                                                      "totalSwapSpace": 12195983360},
                            "hudson.node_monitors.ArchitectureMonitor": "Linux (amd64)",
                            "hudson.node_monitors.ResponseTimeMonitor": {"average": 64},
                            "hudson.node_monitors.TemporarySpaceMonitor": {"path": "/tmp", "size": 250172776448},
                            "hudson.node_monitors.DiskSpaceMonitor": {"path": "/home/sal/jenkins",
                                                                      "size": 170472026112},
                            "hudson.node_monitors.ClockMonitor": {"diff": 6736}},
            "numExecutors": 1,
            "offline": False,
            "offlineCause": None,
            "oneOffExecutors": [],
            "temporarilyOffline": False}

    @mock.patch.object(Label, "_poll")
    def setUp(self, label_poll):
        label_poll.return_value = self.LABEL

        self.J = mock.MagicMock()
        self.l = Label('label_testLabel', self.J)

    def testRepr(self):
        self.assertEqual(repr(self.l), '<jenkinsapi.label.Label label_testLabel>')

    def testName(self):
        self.assertEqual(self.l.name, "label_testLabel")

    def testDescription(self):
        self.assertEqual(self.l.description, "A Label")

    @mock.patch.object(Job, '_poll')
    def testGetJobs(self, job_poll):
        job_poll.return_value = self.JOB
        jobs = self.l.get_jobs()
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].name, "testjob")

    @mock.patch.object(Node, '_poll')
    def testGetNodes(self, node_poll):
        node_poll.return_value = self.NODE
        nodes = self.l.get_nodes()
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].name, "thenodeknows")


if __name__ == '__main__':
    unittest.main()
