"""
Extract version information from the latest build.
"""
from jenkinsapi.jenkins import Jenkins


def getSCMInfroFromLatestGoodBuild(url, jobName, username=None, password=None):
    J = Jenkins(url, username, password)
    job = J[jobName]
    lgb = job.get_last_good_build()
    return lgb.get_revision()

if __name__ == '__main__':
    print getSCMInfroFromLatestGoodBuild('http://localhost:8080', 'fooJob')
