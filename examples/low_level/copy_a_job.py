"""
A lower-level implementation of copying a job in Jenkins
"""

import requests
from jenkinsapi.jenkins import Jenkins
from pkg_resources import resource_string
from jenkinsapi_tests.test_utils.random_strings import random_string

J = Jenkins('http://localhost:8080')
jobName = random_string()
jobName2 = '%s_2' % jobName

url = 'http://localhost:8080/createItem?from=%s&name=%s&mode=copy' % (
        jobName, jobName2)

xml = resource_string('examples', 'addjob.xml')
j = J.create_job(jobname=jobName, config=xml)


h = {'Content-Type': 'application/x-www-form-urlencoded'}
response = requests.post(url, data='dysjsjsjs', headers=h)
print response.text.encode('UTF-8')
