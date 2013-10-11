from jenkinsapi.view import View
from jenkinsapi.jenkins import Jenkins
J = Jenkins('http://localhost:8080')
print J.items()
j = J['foo']
j = J.get_job("foo")
b = j.get_last_build()
print b
mjn = b.get_master_job_name()
print(mjn)

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

new_job = J.create_job(name='foo_job', config=EMPTY_JOB_CONFIG)
