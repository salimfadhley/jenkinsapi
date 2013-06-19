'''
System tests for `jenkinsapi.jenkins` module.
'''
import time
import logging
import unittest
from jenkinsapi_tests.systests.base import BaseSystemTest

log = logging.getLogger(__name__)

JOB_CONFIGS = {
'A':"""<?xml version='1.0' encoding='UTF-8'?>
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

'B':"""<?xml version='1.0' encoding='UTF-8'?>
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

'C':"""<?xml version='1.0' encoding='UTF-8'?>
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
    def test_invoke_job_parameterized(self):
        for job_name, job_config in JOB_CONFIGS.items():
            self.jenkins.create_job(job_name, job_config)

        self.jenkins['A'].invoke()


        for _ in range(0,10):
            if not self.jenkins['C'].get_last_completed_buildnumber() > 0:
                log.info('Waiting for the third test to complete')
                time.sleep(2)
            else:
                break
        else:
            self.fail('Jenkins took too long to run these jobs')

        self.assertTrue(self.jenkins['C'].get_upstream_jobs(), self.jenkins['B'])
        self.assertTrue(self.jenkins['B'].get_upstream_jobs(), self.jenkins['A'])

        self.assertTrue(self.jenkins['A'].get_downstream_jobs(), self.jenkins['B'])
        self.assertTrue(self.jenkins['B'].get_downstream_jobs(), self.jenkins['C'])

if __name__ == '__main__':
    logging.basicConfig()
    unittest.main()
