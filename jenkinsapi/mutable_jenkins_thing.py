"""
Module for MutableJenkinsThing
"""


class MutableJenkinsThing(object):

    """
    A mixin for certain mutable objects which can be renamed and deleted.
    """

    def get_delete_url(self):
        return '%s/doDelete' % self.baseurl

    def get_rename_url(self):
        return '%s/doRename' % self.baseurl
