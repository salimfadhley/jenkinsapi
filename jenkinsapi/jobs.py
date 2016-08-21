"""
This module implements the Jobs class, which is intended to be a container-like
interface for all of the jobs defined on a single Jenkins server.
"""
import logging
from jenkinsapi.job import Job
from jenkinsapi.custom_exceptions import JenkinsAPIException, UnknownJob

log = logging.getLogger(__name__)


class Jobs(object):

    """
    This class provides a container-like API which gives
    access to all jobs defined on the Jenkins server. It behaves
    like a dict in which keys are Job-names and values are actual
    jenkinsapi.Job objects.
    """

    def __init__(self, jenkins):
        self.jenkins = jenkins
        self._data = []

    def _del_data(self, job_name):
        if len(self._data) == 0:
            return
        for num, job_data in enumerate(self._data):
            if job_data['name'] == job_name:
                del self._data[num]
                return

    def __len__(self):
        return len(self.keys())

    def poll(self, tree='jobs[name,color,url]'):
        return self.jenkins.poll(tree=tree)

    def __delitem__(self, job_name):
        """
        Delete a job by name
        :param str job_name: name of a existing job
        :raises JenkinsAPIException:  When job is not deleted
        """
        if job_name in self:
            try:
                delete_job_url = self[job_name].get_delete_url()
                self.jenkins.requester.post_and_confirm_status(
                    delete_job_url,
                    data='some random bytes...'
                )

                self._del_data(job_name)
            except JenkinsAPIException:
                # Sometimes jenkins throws NPE when removing job
                # It removes job ok, but it is good to be sure
                # so we re-try if job was not deleted
                if job_name in self:
                    delete_job_url = self[job_name].get_delete_url()
                    self.jenkins.requester.post_and_confirm_status(
                        delete_job_url,
                        data='some random bytes...'
                    )
                    self._del_data(job_name)

    def __setitem__(self, key, value):
        """
        Create Job

        :param str key:     Job name
        :param str value:   XML configuration of the job

        .. code-block:: python
        api = Jenkins('http://localhost:8080/')
        new_job = api.jobs['my_new_job'] = config_xml
        """
        return self.create(key, value)

    def __getitem__(self, job_name):
        if job_name in self:
            job_data = [job_row for job_row in self._data
                        if job_row['name'] == job_name][0]
            return Job(job_data['url'], job_data['name'], self.jenkins)
        else:
            raise UnknownJob(job_name)

    def iteritems(self):
        """
        Iterate over the names & objects for all jobs
        """
        for job in self.itervalues():
            yield job.name, job

    def __contains__(self, job_name):
        """
        True if job_name exists in Jenkins
        """
        return job_name in self.keys()

    def iterkeys(self):
        """
        Iterate over the names of all available jobs
        """
        if len(self._data) == 0:
            self._data = self.poll().get('jobs', [])
        for row in self._data:
            yield row['name']

    def itervalues(self):
        """
        Iterate over all available jobs
        """
        if len(self._data) == 0:
            self._data = self.poll().get('jobs', [])
        for row in self._data:
            yield Job(row['url'], row['name'], self.jenkins)

    def keys(self):
        """
        Return a list of the names of all jobs
        """
        return list(self.iterkeys())

    def create(self, job_name, config):
        """
        Create a job

        :param str jobname: Name of new job
        :param str config: XML configuration of new job
        :returns Job: new Job object
        """
        if job_name in self:
            return self[job_name]

        if config is None or len(config) == 0:
            raise JenkinsAPIException('Job XML config cannot be empty')

        params = {'name': job_name}
        try:
            if isinstance(
                    config, unicode):  # pylint: disable=undefined-variable
                config = str(config)
        except NameError:
            # Python2 already a str
            pass

        self.jenkins.requester.post_xml_and_confirm_status(
            self.jenkins.get_create_url(),
            data=config,
            params=params
        )
        # Reset to get it refreshed from Jenkins
        self._data = []

        return self[job_name]

    def copy(self, job_name, new_job_name):
        """
        Copy a job
        :param str job_name: Name of an existing job
        :param new_job_name: Name of new job
        :returns Job: new Job object
        """
        params = {'name': new_job_name,
                  'mode': 'copy',
                  'from': job_name}

        self.jenkins.requester.post_and_confirm_status(
            self.jenkins.get_create_url(),
            params=params,
            data='')

        self._data = []

        return self[new_job_name]

    def rename(self, job_name, new_job_name):
        """
        Rename a job

        :param str job_name: Name of an existing job
        :param str new_job_name: Name of new job
        :returns Job: new Job object
        """
        params = {'newName': new_job_name}
        rename_job_url = self[job_name].get_rename_url()
        self.jenkins.requester.post_and_confirm_status(
            rename_job_url, params=params, data='')

        self._data = []

        return self[new_job_name]

    def build(self, job_name, params=None, **kwargs):
        """
        Executes build of a job

        :param str job_name:    Job name
        :param dict params:     Job parameters
        :param kwargs:          Parameters for Job.invoke() function
        :returns QueueItem:     Object to track build progress
        """
        if params is not None:
            assert isinstance(params, dict)
            return self[job_name].invoke(build_params=params, **kwargs)
        else:
            return self[job_name].invoke(**kwargs)
