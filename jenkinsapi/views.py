"""
Module for jenkinsapi Views
"""

import logging
import json
from jenkinsapi.view import View

log = logging.getLogger(__name__)


class Views(object):
    """
    An abstraction on a Jenkins object's views
    """
    LIST_VIEW = 'hudson.model.ListView'
    NESTED_VIEW = 'hudson.plugins.nested_view.NestedView'
    MY_VIEW = 'hudson.model.MyView'
    DASHBOARD_VIEW = 'hudson.plugins.view.dashboard.Dashboard'
    PIPELINE_VIEW = 'au.com.centrumsystems.hudson.plugin.buildpipeline.BuildPipelineView'

    def __init__(self, jenkins):
        self.jenkins = jenkins

    def __len__(self):
        return len(self.keys())

    def __delitem__(self, view_name):
        if view_name == 'All':
            raise ValueError('Cannot delete this view: %s' % view_name)

        if view_name in self:
            self[view_name].delete()
            self.jenkins.poll()

    def __setitem__(self, view_name, job_names_list):
        new_view = self.create(view_name)
        if isinstance(job_names_list, str):
            job_names_list = [job_names_list]
        for job_name in job_names_list:
            if not new_view.add_job(job_name):
                # Something wrong - delete view
                del self[new_view]
                raise TypeError('Job %s does not exist in Jenkins' % job_name)

    def __getitem__(self, view_name):
        for row in self.jenkins._data.get('views', []):
            if row['name'] == view_name:
                return View(row['url'], row['name'], self.jenkins)

    def iteritems(self):
        """
        Get the names & objects for all views
        """
        self.jenkins.poll()
        for row in self.jenkins._data.get('views', []):
            name = row['name']
            url = row['url']

            yield name, View(url, name, self.jenkins)

    def __contains__(self, view_name):
        """
        True if view_name is the name of a defined view
        """
        return view_name in self.keys()

    def iterkeys(self):
        """
        Get the names of all available views
        """
        for row in self.jenkins._data.get('views', []):
            yield row['name']

    def keys(self):
        """
        Return a list of the names of all views
        """
        return list(self.iterkeys())

    def create(self, view_name, view_type=LIST_VIEW):
        """
        Create a view
        :param view_name: name of new view, str
        :param person: Person name (to create personal view), str
        :return: new View obj or None if view was not created
        """
        log.info(msg='Creating "%s" view "%s"' % (view_type, view_name))
        #url = urlparse.urljoin(self.baseurl, "user/%s/my-views/" % person) if person else self.baseurl

        if view_name in self:
            log.warn(msg='View "%s" already exists' % view_name)
            return self[view_name]

        url = '%s/createView' % self.jenkins.baseurl
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            "name": view_name,
            "mode": view_type,
            "Submit": "OK",
            "json": json.dumps({"name": view_name, "mode": view_type})
        }

        self.jenkins.requester.post_and_confirm_status(url, data=data, headers=headers)
        self.jenkins.poll()
        return self[view_name]
