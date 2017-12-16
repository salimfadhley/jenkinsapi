"""
Example of using CrumbRequester - when CSRF protection is enable in Jenkins
"""
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.utils.crumb_requester import CrumbRequester

jenkins = Jenkins('http://localhost:8080', user='admin', password='password',
                  requester=CrumbRequester(
                       'http://localhost:8080',
                       user='admin',
                       password='password'
                  ))

for job_name in jenkins.jobs:
    print job_name
