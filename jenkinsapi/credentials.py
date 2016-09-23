"""
This module implements the Credentials class, which is intended to be a
container-like interface for all of the Global credentials defined on a single
Jenkins node.
"""
import logging
try:
    from urllib import urlencode
except ImportError:
    # Python3
    from urllib.parse import urlencode
from jenkinsapi.credential import Credential
from jenkinsapi.credential import UsernamePasswordCredential
from jenkinsapi.credential import SecretTextCredential
from jenkinsapi.credential import SSHKeyCredential
from jenkinsapi.jenkinsbase import JenkinsBase
from jenkinsapi.custom_exceptions import JenkinsAPIException

log = logging.getLogger(__name__)


class Credentials(JenkinsBase):
    """
    This class provides a container-like API which gives
    access to all global credentials on a Jenkins node.

    Returns a list of Credential Objects.
    """
    def __init__(self, baseurl, jenkins_obj):
        self.baseurl = baseurl
        self.jenkins = jenkins_obj
        JenkinsBase.__init__(self, baseurl)

        self.credentials = self._data['credentials']

    def _poll(self, tree=None):
        url = self.python_api_url(self.baseurl) + '?depth=2'
        data = self.get_data(url, tree=tree)
        credentials = data['credentials']
        for cred_id, cred_dict in credentials.items():
            cred_dict['credential_id'] = cred_id
            credentials[cred_id] = self._make_credential(cred_dict)

        return data

    def __str__(self):
        return 'Global Credentials @ %s' % self.baseurl

    def get_jenkins_obj(self):
        return self.jenkins

    def __iter__(self):
        for cred in self.credentials.values():
            yield cred.description

    def __contains__(self, description):
        return description in self.keys()

    def iterkeys(self):
        return self.__iter__()

    def keys(self):
        return list(self.iterkeys())

    def iteritems(self):
        for cred in self.credentials.values():
            yield cred.description, cred

    def __getitem__(self, description):
        for cred in self.credentials.values():
            if cred.description == description:
                return cred

        raise KeyError('Credential with description "%s" not found'
                       % description)

    def __len__(self):
        return len(self.keys())

    def __setitem__(self, description, credential):
        """
        Creates Credential in Jenkins using username, password and description
        Description must be unique in Jenkins instance
        because it is used to find Credential later.

        If description already exists - this method is going to update
        existing Credential

        :param str description: Credential description
        :param tuple credential_tuple: (username, password, description) tuple.
        """
        if description not in self:
            params = credential.get_attributes()
            url = (
                '%s/createCredentials'
                % self.baseurl
            )
        else:
            raise JenkinsAPIException('Updating credentials is not supported '
                                      'by jenkinsapi')

        try:
            self.jenkins.requester.post_and_confirm_status(
                url, params={}, data=urlencode(params)
            )
        except JenkinsAPIException as jae:
            raise JenkinsAPIException('Latest version of Credentials '
                                      'plugin is required to be able '
                                      'to create/update credentials. '
                                      'Original exception: %s' % str(jae))

        self.poll()
        self.credentials = self._data['credentials']
        if description not in self:
            raise JenkinsAPIException('Problem creating/updating credential.')

    def get(self, item, default):
        return self[item] if item in self else default

    def __delitem__(self, description):
        if description not in self:
            raise KeyError(
                'Credential with description "%s" not found' % description)
        params = {
            'Submit': 'OK',
            'json': {}
        }
        url = ('%s/credential/%s/doDelete'
               % (self.baseurl, self[description].credential_id))
        try:
            self.jenkins.requester.post_and_confirm_status(
                url, params={}, data=urlencode(params)
            )
        except JenkinsAPIException as jae:
            raise JenkinsAPIException('Latest version of Credentials '
                                      'required to be able to create '
                                      'credentials. Original exception: %s'
                                      % str(jae))
        self.poll()
        self.credentials = self._data['credentials']
        if description in self:
            raise JenkinsAPIException('Problem deleting credential.')

    def _make_credential(self, cred_dict):
        if cred_dict['typeName'] == 'Username with password':
            cr = UsernamePasswordCredential(cred_dict)
        elif cred_dict['typeName'] == 'SSH Username with private key':
            cr = SSHKeyCredential(cred_dict)
        elif cred_dict['typeName'] == 'Secret text':
            cr = SecretTextCredential(cred_dict)
        else:
            cr = Credential(cred_dict)

        return cr


class Credentials2x(Credentials):
    """
    This class provides a container-like API which gives
    access to all global credentials on a Jenkins node.

    Returns a list of Credential Objects.
    """
    def _poll(self, tree=None):
        url = self.python_api_url(self.baseurl) + '?depth=2'
        data = self.get_data(url, tree=tree)
        credentials = data['credentials']
        new_creds = {}
        for cred_dict in credentials:
            cred_dict['credential_id'] = cred_dict['id']
            new_creds[cred_dict['id']] = self._make_credential(cred_dict)

        data['credentials'] = new_creds

        return data
