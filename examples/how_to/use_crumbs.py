"""
Example of using CrumbRequester - when CSRF protection is enable in Jenkins
"""
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.utils.crumb_requester import CrumbRequester

jenkins = Jenkins('http://localhost:8080', username='admin', password='password',
                  requester=CrumbRequester(
                       baseurl='http://localhost:8080',
                       username='admin',
                       password='password'
                  ))

for job_name in jenkins.jobs:
    print job_name
