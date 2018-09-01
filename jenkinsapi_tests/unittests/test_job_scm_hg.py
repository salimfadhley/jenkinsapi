import mock
# To run unittests on python 2.6 please use unittest2 library
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from jenkinsapi import config
from jenkinsapi.job import Job
from jenkinsapi.jenkinsbase import JenkinsBase


# TODO: Make JOB_DATA to be one coming from Hg job
class TestHgJob(unittest.TestCase):
    JOB_DATA = {
        "actions": [],
        "description": "test job",
        "displayName": "foo",
        "displayNameOrNull": None,
        "name": "foo",
        "url": "http://halob:8080/job/foo/",
        "buildable": True,
        "builds": [
            {"number": 3, "url": "http://halob:8080/job/foo/3/"},
            {"number": 2, "url": "http://halob:8080/job/foo/2/"},
            {"number": 1, "url": "http://halob:8080/job/foo/1/"}
        ],
        "color": "blue",
        "firstBuild": {"number": 1, "url": "http://halob:8080/job/foo/1/"},
        "healthReport": [
            {"description": "Build stability: No recent builds failed.",
             "iconUrl": "health-80plus.png",
             "score": 100}
        ],
        "inQueue": False,
        "keepDependencies": False,
        # build running
        "lastBuild": {"number": 4, "url": "http://halob:8080/job/foo/4/"},
        "lastCompletedBuild": {"number": 3, "url": "http://halob:8080/job/foo/3/"},
        "lastFailedBuild": None,
        "lastStableBuild": {"number": 3, "url": "http://halob:8080/job/foo/3/"},
        "lastSuccessfulBuild": {"number": 3, "url": "http://halob:8080/job/foo/3/"},
        "lastUnstableBuild": None,
        "lastUnsuccessfulBuild": None,
        "nextBuildNumber": 4,
        "property": [],
        "queueItem": None,
        "concurrentBuild": False,
        "downstreamProjects": [],
        "scm": {},
        "upstreamProjects": []
    }

    URL_DATA = {'http://halob:8080/job/foo/%s' % config.JENKINS_API: JOB_DATA}

    def fakeGetData(self, url, *args, **kwargs):
        try:
            return TestHgJob.URL_DATA[url]
        except KeyError:
            raise Exception("Missing data for %s" % url)

    @mock.patch.object(JenkinsBase, 'get_data', fakeGetData)
    def setUp(self):
        self.J = mock.MagicMock()  # Jenkins object
        self.j = Job('http://halob:8080/job/foo/', 'foo', self.J)

    def configtree_with_branch(self):
        config_node = '''
        <project>
        <scm class="hudson.plugins.mercurial.MercurialSCM" plugin="mercurial@1.42">
        <source>http://cm5/hg/sandbox/v01.0/int</source>
        <modules/>
        <branch>testme</branch>
        <clean>false</clean>
        <browser class="hudson.plugins.mercurial.browser.HgWeb">
        <url>http://cm5/hg/sandbox/v01.0/int/</url>
        </browser>
        </scm>
        </project>
        '''
        return config_node

    def configtree_with_default_branch(self):
        config_node = '''
        <project>
        <scm class="hudson.plugins.mercurial.MercurialSCM" plugin="mercurial@1.42">
        <source>http://cm5/hg/sandbox/v01.0/int</source>
        <modules/>
        <clean>false</clean>
        <browser class="hudson.plugins.mercurial.browser.HgWeb">
        <url>http://cm5/hg/sandbox/v01.0/int/</url>
        </browser>
        </scm>
        </project>
        '''
        return config_node

    @mock.patch.object(Job, 'get_config', configtree_with_branch)
    def test_hg_attributes(self):
        expected_url = ['http://cm5/hg/sandbox/v01.0/int']
        self.assertEqual(self.j.get_scm_type(), 'hg')
        self.assertEqual(self.j.get_scm_url(), expected_url)
        self.assertEqual(self.j.get_scm_branch(), ['testme'])

    @mock.patch.object(Job, 'get_config', configtree_with_default_branch)
    def test_hg_attributes_default_branch(self):
        self.assertEqual(self.j.get_scm_branch(), ['default'])


if __name__ == '__main__':
    unittest.main()
