import logging
logging.basicConfig()

from jenkinsapi.jenkins import Jenkins
from pkg_resources import resource_string
J = Jenkins('http://localhost:8080')
jobName = 'foo_job2'
xml = resource_string('examples', 'addjob.xml')

print xml

j = J.create_job(jobname=jobName, config=xml)

j2 = J[jobName]
print j

# Delete job
J.delete_job(jobName)
