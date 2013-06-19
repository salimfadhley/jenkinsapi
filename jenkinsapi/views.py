import json
from jenkinsapi.view import View
from jenkinsapi.exceptions import UnknownView

class Views(object):
    """
    An abstraction on a Jenkins object's views
    """

    def __init__(self, jenkins):
        self.jenkins = jenkins

    def __len__(self):
        return len(self.keys())

    def __delitem__(self, view_name):
        if view_name == 'All':
            raise ValueError('Cannot delete this view: %s' % view_name)

        self[view_name].delete()
        self.jenkins.poll

    def __setitem__(self, name, value):
        raise NotImplementedError()

    def __getitem__(self, view_name):
        for row in self.jenkins._data['views']:
            if row['name'] == view_name:
                return View(
                    row['url'],
                    row['name'],
                    self.jenkins)
        raise UnknownView(view_name)

    def __iteritems__(self):
        """
        Get the names & objects for all views
        """
        self.jenkins.poll()
        for row in self.jenkins._data['views']:
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
        for row in self.jenkins._data['views']:
            yield row['name']

    def keys(self):
        """
        Return a list of the names of all views
        """
        return list(self.iterkeys())

    def delete_view_by_url(self, str_url):
        url = "%s/doDelete" % str_url
        response = self.requester.get_url(url, data='')
        self.jenkins.poll()
        return self

    def create(self, str_view_name):
        """
        Create a view
        :param str_view_name: name of new view, str
        :param person: Person name (to create personal view), str
        :return: new View obj or None if view was not created
        """
        #url = urlparse.urljoin(self.baseurl, "user/%s/my-views/" % person) if person else self.baseurl
        try:
            return self[str_view_name]
        except KeyError:
            pass
        url = '%s/createView' % self.jenkins.baseurl
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            "name": str_view_name,
            "mode": "hudson.model.ListView",
            "Submit": "OK",
            "json": json.dumps({"name": str_view_name, "mode": "hudson.model.ListView"})
        }

        self.jenkins.requester.post_and_confirm_status(url, data=data, headers=headers)
        self.jenkins.poll()
        return self[str_view_name]
