"""
Queue module for jenkinsapi
"""

from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.custom_exceptions import UnknownQueueItem
import logging

log = logging.getLogger(__name__)


class Queue(JenkinsBase):
    """
    Class that represents the Jenkins queue
    """

    def __init__(self, baseurl, jenkins_obj):
        """
        Init the Jenkins queue object
        :param baseurl: basic url for the queue
        :param jenkins_obj: ref to the jenkins obj
        """
        self.jenkins = jenkins_obj
        JenkinsBase.__init__(self, baseurl)

    def __str__(self):
        return self.baseurl

    def get_jenkins_obj(self):
        return self.jenkins

    def iteritems(self):
        for item in self._data['items']:
            yield item['id'], QueueItem(self.jenkins, **item)

    def iterkeys(self):
        for item in self._data['items']:
            yield item['id']

    def iterivalues(self):
        for item in self._data['items']:
            yield QueueItem(self.jenkins, **item)

    def keys(self):
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())

    def __len__(self):
        return len(self._data['items'])

    def __getitem__(self, item_id):
        self_as_dict = dict(self.iteritems())
        if item_id in self_as_dict:
            return self_as_dict[item_id]
        else:
            raise UnknownQueueItem(item_id)

    def get_queue_items_for_job(self, job_name):
        if not job_name:
            return [QueueItem(**item) for item in self._data['items']]
        else:
            return [QueueItem(**item) for item in self._data['items']
                    if item['task']['name'] == job_name]

    def delete_item(self, queue_item):
        self.delete_item_by_id(queue_item.id)

    def delete_item_by_id(self, item_id):
        deleteurl = '%s/cancelItem?id=%s' % (self.baseurl, item_id)
        self.get_jenkins_obj().requester.post_url(deleteurl)


class QueueItem(object):
    """
    Flexible class to handle queue items. If the Jenkins API changes this support
    those changes
    """

    def __init__(self, jenkins, **kwargs):
        self.jenkins = jenkins
        self.__dict__.update(kwargs)

    def get_job(self):
        """
        Return the job associated with this queue item
        """
        return self.jenkins[self.task['name']]

    def __repr__(self):
        return "<%s.%s %s>" % (self.__class__.__module__, self.__class__.__name__, str(self))

    def __str__(self):
        return "%s #%i" % (self.task['name'], self.id)
