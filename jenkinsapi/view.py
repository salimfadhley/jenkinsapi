from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.job import Job
import urllib

class View(JenkinsBase):

    def __init__(self, url, name, jenkins_obj):
        self.name = name
        self.jenkins_obj = jenkins_obj
        JenkinsBase.__init__(self, url)

    def __str__(self):
        return self.name

    def __getitem__(self, str_job_id ):
        assert isinstance( str_job_id, str )
        api_url = self.python_api_url( self.get_job_url( str_job_id ) )
        return Job( api_url, str_job_id, self.jenkins_obj )

    def keys(self):
        return self.get_job_dict().keys()

    def iteritems(self):
        for name, url in self.get_job_dict().iteritems():
            api_url = self.python_api_url( url )
            yield name, Job( api_url, name, self.jenkins_obj )

    def values(self):
        return [ a[1] for a in self.iteritems() ]

    def items(self):
        return [ a for a in self.iteritems() ]

    def _get_jobs( self ):
        if not self._data.has_key( "jobs" ):
            pass
        else:
            for viewdict in self._data["jobs"]:
                yield viewdict["name"], viewdict["url"]

    def get_job_dict(self):
        return dict( self._get_jobs() )

    def __len__(self):
        return len( self.get_job_dict().keys() )

    def get_job_url( self, str_job_name ):
        try:
            job_dict = self.get_job_dict()
            return job_dict[ str_job_name ]
        except KeyError:
            #noinspection PyUnboundLocalVariable
            all_views = ", ".join( job_dict.keys() )
            raise KeyError("Job %s is not known - available: %s" % ( str_job_name, all_views ) )

    def get_jenkins_obj(self):
        return self.jenkins_obj

    def add_job(self, str_job_name):
        if str_job_name in self.get_job_dict():
            return "Job %s has in View %s" %(str_job_name, self.name)
        elif not self.get_jenkins_obj().has_job(str_job_name):
            return "Job %s is not known - available: %s" % ( str_job_name, ", ".join(self.get_jenkins_obj().get_jobs_list()))
        else:
            def get_job_url(name):
                return self.jenkins_obj.get_job(name).baseurl
            jobs = self._data.setdefault('jobs', [])
            jobs.append({'name': str_job_name, 'url': get_job_url(str_job_name)})
            data = {
                "description":"",
                "statusFilter":"",
                "useincluderegex":"on",
                "includeRegex":"",
                "columns": [{"stapler-class": "hudson.views.StatusColumn", "kind": "hudson.views.StatusColumn"}, 
                            {"stapler-class": "hudson.views.WeatherColumn", "kind": "hudson.views.WeatherColumn"}, 
                            {"stapler-class": "hudson.views.JobColumn", "kind": "hudson.views.JobColumn"}, 
                            {"stapler-class": "hudson.views.LastSuccessColumn", "kind": "hudson.views.LastSuccessColumn"}, 
                            {"stapler-class": "hudson.views.LastFailureColumn", "kind": "hudson.views.LastFailureColumn"}, 
                            {"stapler-class": "hudson.views.LastDurationColumn", "kind": "hudson.views.LastDurationColumn"}, 
                            {"stapler-class": "hudson.views.BuildButtonColumn", "kind": "hudson.views.BuildButtonColumn"}],
                "Submit":"OK",
                }
            data["name"] = self.name
            for job in self.get_job_dict().keys():
                data[job]='on'
            data['json'] = data.copy()
            self.post_data('%sconfigSubmit' % self.baseurl, urllib.urlencode(data))
            return "Job %s is add in View %s successful" % (str_job_name, self.baseurl)

    def _get_nested_views(self):
        if not self._data.has_key( "views" ):
            pass
        else:
            for viewdict in self._data["views"]:
                yield viewdict["name"], viewdict["url"]
                
    def get_nested_view_dict(self):
        return dict( self._get_nested_views() )

    def id(self):
        """
        Calculate an ID for this object.
        """
        return "%s.%s" % ( self.className, self.name )
