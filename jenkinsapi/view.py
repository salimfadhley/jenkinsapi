import urllib
import logging

from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.job import Job


log = logging.getLogger(__name__)


class View(JenkinsBase):
    def __init__(self, url, name, jenkins_obj):
        self.name = name
        self.jenkins_obj = jenkins_obj
        JenkinsBase.__init__(self, url)
        self.deleted = False

    def __str__(self):
        return self.name

    def __getitem__(self, job_name):
        assert isinstance(job_name, str)
        api_url = self.python_api_url(self.get_job_url(job_name))
        return Job(api_url, job_name, self.jenkins_obj)

    def __contains__(self, job_name):
        """
        True if view_name is the name of a defined view
        """
        return job_name in self.keys()

    def delete(self):
        """
        Remove this view object
        """
        url = "%s/doDelete" % self.baseurl
        self.jenkins_obj.requester.post_and_confirm_status(url, data='')
        self.jenkins_obj.poll()
        self.deleted = True

    def keys(self):
        return self.get_job_dict().keys()

    def iteritems(self):
        for name, url in self.get_job_dict().iteritems():
            api_url = self.python_api_url(url)
            yield name, Job(api_url, name, self.jenkins_obj)

    def values(self):
        return [a[1] for a in self.iteritems()]

    def items(self):
        return [a for a in self.iteritems()]

    def _get_jobs(self):
        if not 'jobs' in self._data:
            pass
        else:
            for viewdict in self._data["jobs"]:
                yield viewdict["name"], viewdict["url"]

    def get_job_dict(self):
        return dict(self._get_jobs())

    def __len__(self):
        return len(self.get_job_dict().keys())

    def get_job_url(self, str_job_name):
        try:
            job_dict = self.get_job_dict()
            return job_dict[str_job_name]
        except KeyError:
            #noinspection PyUnboundLocalVariable
            all_views = ", ".join(job_dict.keys())
            raise KeyError("Job %s is not known - available: %s" % (str_job_name, all_views))

    def get_jenkins_obj(self):
        return self.jenkins_obj

    def add_job(self, str_job_name, job=None):
        """
        Add job to a view

        :param str_job_name: name of the job to be added
        :param job: Job object to be added
        :return: True if job has been added, False if job already exists or
         job not known to Jenkins
        """
        if not job:
            if str_job_name in self.get_job_dict():
                log.warn('Job %s is already in the view %s' %
                         (str_job_name, self.name))
                return False
            else:
                # Since this call can be made from nested view,
                # which doesn't have any jobs, we can miss existing job
                # Thus let's create top level Jenkins and ask him
                # http://jenkins:8080/view/CRT/view/CRT-FB/view/CRT-SCRT-1301/
                top_jenkins = self.get_jenkins_obj().get_jenkins_obj_from_url(
                    self.baseurl.split('view/')[0])
                if not top_jenkins.has_job(str_job_name):
                    log.error('Job "%s" is not known to Jenkins' % str_job_name)
                    return False
                else:
                    job = top_jenkins.get_job(str_job_name)

        log.info('Creating job %s in view %s' % (str_job_name, self.name))
        data = {
            "description": "",
            "statusFilter": "",
            "useincluderegex": "on",
            "includeRegex": "",
            "columns": [{"stapler-class": "hudson.views.StatusColumn",
                         "kind": "hudson.views.StatusColumn"},
                        {"stapler-class": "hudson.views.WeatherColumn",
                         "kind": "hudson.views.WeatherColumn"},
                        {"stapler-class": "hudson.views.JobColumn",
                         "kind": "hudson.views.JobColumn"},
                        {"stapler-class": "hudson.views.LastSuccessColumn",
                         "kind": "hudson.views.LastSuccessColumn"},
                        {"stapler-class": "hudson.views.LastFailureColumn",
                         "kind": "hudson.views.LastFailureColumn"},
                        {"stapler-class": "hudson.views.LastDurationColumn",
                         "kind": "hudson.views.LastDurationColumn"},
                        {"stapler-class": "hudson.views.BuildButtonColumn",
                         "kind": "hudson.views.BuildButtonColumn"}],
            "Submit": "OK",
        }
        data["name"] = self.name
        # Add existing jobs (if any)
        for job_name in self.get_job_dict().keys():
            data[job_name] = 'on'

        # Add new job
        data[job.name] = 'on'

        data['json'] = data.copy()
        data = urllib.urlencode(data)
        self.get_jenkins_obj().requester.post_and_confirm_status(
            '%s/configSubmit' % self.baseurl, data=data)
        self.poll()
        log.debug('Job "%s" has been added to a view "%s"' %
                  (job.name, self.name))
        return True

    def _get_nested_views(self):
        if not 'views' in self._data:
            pass
        else:
            for viewdict in self._data["views"]:
                yield viewdict["name"], viewdict["url"]

    def get_nested_view_dict(self):
        return dict(self._get_nested_views())

    @property
    def views(self):
        return self.get_jenkins_obj().get_jenkins_obj_from_url(self.baseurl).views
