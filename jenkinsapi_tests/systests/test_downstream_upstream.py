'''
System tests for `jenkinsapi.jenkins` module.
'''
import time
import logging
import unittest
from jenkinsapi.custom_exceptions import NoBuildData
from jenkinsapi_tests.systests.base import BaseSystemTest

log = logging.getLogger(__name__)

JOB_CONFIGS = {
    'A': """<?xml version='1.0' encoding='UTF-8'?>
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
  <publishers>
    <hudson.tasks.BuildTrigger>
      <childProjects>B</childProjects>
      <threshold>
        <name>SUCCESS</name>
        <ordinal>0</ordinal>
        <color>BLUE</color>
      </threshold>
    </hudson.tasks.BuildTrigger>
  </publishers>
  <buildWrappers/>
</project>""",

    'B': """<?xml version='1.0' encoding='UTF-8'?>
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
  <publishers>
    <hudson.tasks.BuildTrigger>
      <childProjects>C</childProjects>
      <threshold>
        <name>SUCCESS</name>
        <ordinal>0</ordinal>
        <color>BLUE</color>
      </threshold>
    </hudson.tasks.BuildTrigger>
  </publishers>
  <buildWrappers/>
</project>""",

    'C': """<?xml version='1.0' encoding='UTF-8'?>
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
</project>"""

}


class TestDownstreamUpstream(BaseSystemTest):
    DELAY = 2

    def test_stream_relationship(self):
        """
        Can we keep track of the relationships between upstream & downstream jobs?
        """
        for job_name, job_config in JOB_CONFIGS.items():
            self.jenkins.create_job(job_name, job_config)

        self.jenkins['A'].invoke()

        for _ in xrange(10):
            try:
                self.jenkins['C'].get_last_completed_buildnumber() > 0
            except NoBuildData:
                log.info("Waiting %i seconds for until the final job has run", self.DELAY)
                time.sleep(self.DELAY)
            else:
                break
        else:
            self.fail('Jenkins took too long to run these jobs')

        self.assertTrue(self.jenkins[
                        'C'].get_upstream_jobs(), self.jenkins['B'])
        self.assertTrue(self.jenkins[
                        'B'].get_upstream_jobs(), self.jenkins['A'])

        self.assertTrue(self.jenkins[
                        'A'].get_downstream_jobs(), self.jenkins['B'])
        self.assertTrue(self.jenkins[
                        'B'].get_downstream_jobs(), self.jenkins['C'])

if __name__ == '__main__':
    logging.basicConfig()
    unittest.main()
