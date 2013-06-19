import unittest
from jenkinsapi.jenkins import Jenkins


EMPTY_JOB_CONFIG = '''\
<?xml version='1.0' encoding='UTF-8'?>
<project>
  <actions/>
  <description></description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <scm class="hudson.scm.NullSCM"/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers class="vector"/>
  <concurrentBuild>false</concurrentBuild>
  <builders/>
  <publishers/>
  <buildWrappers/>
</project>
'''


class BaseSystemTest(unittest.TestCase):

    def setUp(self):
        self.jenkins = Jenkins('http://localhost:8080')
        self._delete_all_jobs()
        self._delete_all_views()

    def tearDown(self):
        pass

    def _delete_all_jobs(self):
        self.jenkins.poll()
        for name in self.jenkins.get_jobs_list():
            self.jenkins.delete_job(name)

    def _delete_all_views(self):
        all_view_names = self.jenkins.views().keys()[1:]
        for name in all_view_names:
            del self.jenkins.views()[name]

    def _create_job(self, name='whatever', config=EMPTY_JOB_CONFIG):
        job = self.jenkins.create_job(name, config)
        self.jenkins.poll()
        return job

    def assertJobIsPresent(self, name):
        self.jenkins.poll()
        self.assertTrue(name in self.jenkins,
                        'Job %r is absent in jenkins.' % name)

    def assertJobIsAbsent(self, name):
        self.jenkins.poll()
        self.assertTrue(name not in self.jenkins,
                        'Job %r is present in jenkins.' % name)
