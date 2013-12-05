"""
Module for jenkinsapi Label
"""
from jenkinsapi.jenkinsbase import JenkinsBase


class Label(JenkinsBase):
    """
    Represents a jenkins Label.

    Labels are used in jenkins to associate nodes and jobs together. The `Label  class offers a way to discover nodes
    that share a label, and jobs that have some tie to a label.

    To get the names of nodes and jobs for a label named foo you could do the following. Note that `nodes` and `jobs`
    properties return lists of strings, not their corresponding objects. This is to prevent too many queries to the
    master if an extremely generic label (for example i386) were used.

    >>> from jenkinsapi.jenkins import Jenkins
    >>> from jenkinsapi.label import Label
    >>> J = Jenkins("http://example.com")
    >>> label_foo = Label("foo", J)
    >>> label_foo.description
    "A dummy label. Please don't use this on projects."
    >>> label_foo.jobs
    ['job1', 'job2']
    >>> label_foo.nodes
    ['node1', 'node2']

    Labels can also be retrieved using `Node.get_labels` from a node object.

    >>> N = J.get_node("node1")
    >>> labels = N.get_labels()
    >>> labels
    [<jenkinsapi.label.Label foo>, <jenkinsapi.label.Label node1>]
    >>> labels[0].jobs
    ['job1', 'job2']

    Since node names are valid labels when used in a jobs label expression they are included by default in the list
    of labels returned by `Node.get_labels`. To exclude the node name as a label you can pass add_host_label=False to
    the function.

    >>> labels_no_host = N.get_labels(add_host_label=False)
    >>> labels_no_host
    [<jenkinsapi.label.Label foo>]
    """

    def __init__(self, name, jenkins_obj):
        """
        Init a label by providing the labels name and the Jenkins environment it is hosted on.
        :param name: the label name as it would appear in jenkins
        :param jenkins_obj: the jenkins environment to look for the label in.
        :return: Label obj
        """
        self.name = name
        self.jenkins = jenkins_obj
        self.baseurl = self.jenkins.baseurl + "/label/" + self.name
        self._nodes = None
        self._jobs = None
        JenkinsBase.__init__(self, self.baseurl)

    def __str__(self):
        return self.name

    def get_jenkins_obj(self):
        return self.jenkins

    @property
    def description(self):
        return self._data['description']

    @property
    def nodes(self):
        if not self._nodes:
            self._get_nodes()
        return self._nodes

    def _get_nodes(self):
        self._nodes = []
        for node in self._data['nodes']:
            self._nodes.append(node['nodeName'])

    @property
    def jobs(self):
        if not self._jobs:
            self._get_jobs()
        return self._jobs

    def _get_jobs(self):
        self._jobs = []
        for job in self._data['tiedJobs']:
            self._jobs.append(job['name'])
