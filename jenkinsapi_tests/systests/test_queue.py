'''
System tests for `jenkinsapi.jenkins` module.
'''
import time
import logging
import unittest
from jenkinsapi.queue import Queue
from jenkinsapi_tests.systests.base import BaseSystemTest
from jenkinsapi_tests.test_utils.random_strings import random_string

log = logging.getLogger(__name__)

JOB_XML = """
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
  <builders>
    <hudson.tasks.Shell>
      <command>ping -c 100 localhost</command>
    </hudson.tasks.Shell>
  </builders>
  <publishers/>
  <buildWrappers/>
</project>""".strip()


class TestQueue(BaseSystemTest):

    def test_get_queue(self):
        q = self.jenkins.get_queue()
        self.assertIsInstance(q, Queue)

    def test_invoke_job_parameterized(self):
        job_names = [random_string() for i in range(5)]
        jobs = []

        for job_name in job_names:
            j = self.jenkins.create_job(job_name, JOB_XML)
            jobs.append(j)
            j.invoke()

        queue = self.jenkins.get_queue()
        reprString = repr(queue)
        self.assertIn(queue.baseurl, reprString)


if __name__ == '__main__':
    logging.basicConfig()
    unittest.main()
