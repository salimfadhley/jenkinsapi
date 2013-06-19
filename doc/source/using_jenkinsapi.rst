Using Jenkins API
=================

JenkinsAPI lets you query the state of a running Jenkins server. It also allows you to change configuration and automate minor tasks on nodes and jobs.

Example 1: Getting version information from a completed build
-------------------------------------------------------------

This is a typical use of JenkinsAPI - it was the very first use I had in mind when the project was first built: In a continuous-integration environment you want to be able to programatically detect the version-control information of the last succsessful build in order to trigger some kind of release process.::

    from jenkinsapi.jenkins import Jenkins

    def getSCMInfroFromLatestGoodBuild(url, jobName, username=None, password=None):
        J = Jenkins(url, username, password)
        job = J[jobName]
        lgb = job.get_last_good_build()
        return lgb.get_revision()

    if __name__ == '__main__':
        print getSCMInfroFromLatestGoodBuild('http://localhost:8080', 'fooJob')

When used with the Git source-control system line 20 will print out something like '8b4f4e6f6d0af609bb77f95d8fb82ff1ee2bba0d' - which looks suspiciously like a Git revision number.


