"""
Module for jenkinsapi Credential class
"""
import logging

log = logging.getLogger(__name__)


class Credential(object):
    """
    Base abstract class for credentials

    Credentials returned from Jenkins don't hold any sensitive information,
    so there is nothing useful can be done with existing credentials
    besides attaching them to Nodes or other objects.

    You can create concrete Credential instance: UsernamePasswordCredential or
    SSHKeyCredential by passing credential's description and credential dict.

    Each class expects specific credential dict, see below.
    """
    # pylint: disable=unused-argument
    def __init__(self, cred_dict):
        """
        Create credential

        :param str description: as Jenkins doesn't allow human friendly names
            for credentials and makes "displayName" itself,
            there is no way to find credential later,
            this field is used to distinguish between credentials
        :param dict cred_dict: dict containing credential information
        """
        self.credential_id = cred_dict.get('credential_id', '')
        self.description = cred_dict['description']
        self.fullname = cred_dict.get('fullName', '')
        self.displayname = cred_dict.get('displayName', '')

    def __str__(self):
        return self.description

    def get_attributes(self):
        pass


class UsernamePasswordCredential(Credential):
    """
    Username and password credential

    Constructor expects following dict:
        {
            'credential_id': str,   Automatically set by jenkinsapi
            'displayName': str,     Automatically set by Jenkins
            'fullName': str,        Automatically set by Jenkins
            'typeName': str,        Automatically set by Jenkins
            'description': str,
            'userName': str,
            'password': str
        }

    When creating credential via jenkinsapi automatic fields not need to be in
    dict
    """
    def __init__(self, cred_dict):
        super(UsernamePasswordCredential, self).__init__(cred_dict)
        if 'typeName' in cred_dict:
            username = cred_dict['displayName'].split('/')[0]
        else:
            username = cred_dict['userName']

        self.username = username
        self.password = cred_dict.get('password', None)

    def get_attributes(self):
        """
        Used by Credentials object to create credential in Jenkins
        """
        c_class = (
            'com.cloudbees.plugins.credentials.impl.'
            'UsernamePasswordCredentialsImpl'
        )
        c_id = '' if self.credential_id is None else self.credential_id
        return {
            'stapler-class': c_class,
            'Submit': 'OK',
            'json': {
                '': '1',
                'credentials': {
                    'stapler-class': c_class,
                    'id': c_id,
                    'username': self.username,
                    'password': self.password,
                    'description': self.description
                }
            }
        }


class SecretTextCredential(Credential):
    """
    Secret text credential

    Constructor expects following dict:
        {
            'credential_id': str,   Automatically set by jenkinsapi
            'displayName': str,     Automatically set by Jenkins
            'fullName': str,        Automatically set by Jenkins
            'typeName': str,        Automatically set by Jenkins
            'description': str,
            'secret': str,
        }

    When creating credential via jenkinsapi automatic fields not need to be in
    dict
    """

    def __init__(self, cred_dict):
        super(SecretTextCredential, self).__init__(cred_dict)
        self.secret = cred_dict.get('secret', None)

    def get_attributes(self):
        """
        Used by Credentials object to create credential in Jenkins
        """
        c_class = (
            'org.jenkinsci.plugins.plaincredentials.impl.'
            'StringCredentialsImpl'
        )
        c_id = '' if self.credential_id is None else self.credential_id
        return {
            'stapler-class': c_class,
            'Submit': 'OK',
            'json': {
                '': '1',
                'credentials': {
                    'stapler-class': c_class,
                    '$class': c_class,
                    'id': c_id,
                    'secret': self.secret,
                    'description': self.description
                }
            }
        }


class SSHKeyCredential(Credential):
    """
    SSH key credential

    Constructr expects following dict:
        {
            'credential_id': str,   Automatically set by jenkinsapi
            'displayName': str,     Automatically set by Jenkins
            'fullName': str,        Automatically set by Jenkins
            'typeName': str,        Automatically set by Jenkins
            'description': str,
            'userName': str,
            'passphrase': str,      SSH key passphrase,
            'private_key': str      Private SSH key
        }

    private_key value is parsed to find type of credential to create:

    private_key starts with -       the value is private key itself
    private_key starts with /       the value is a path to key
    private_key starts with ~       the value is a key from ~/.ssh

    When creating credential via jenkinsapi automatic fields not need to be in
    dict
    """
    def __init__(self, cred_dict):
        super(SSHKeyCredential, self).__init__(cred_dict)
        if 'typeName' in cred_dict:
            username = cred_dict['displayName'].split(' ')[0]
        else:
            username = cred_dict['userName']

        self.username = username
        self.passphrase = cred_dict.get('passphrase', '')

        if 'private_key' not in cred_dict or cred_dict['private_key'] is None:
            self.key_type = -1
            self.key_value = None
        elif cred_dict['private_key'].startswith('-'):
            self.key_type = 0
            self.key_value = cred_dict['private_key']
        elif cred_dict['private_key'].startswith('/'):
            self.key_type = 1
            self.key_value = cred_dict['private_key']
        elif cred_dict['private_key'].startswith('~'):
            self.key_type = 2
            self.key_value = cred_dict['private_key']
        else:
            raise ValueError('Invalid private_key value')

    def get_attributes(self):
        """
        Used by Credentials object to create credential in Jenkins
        """
        base_class = (
            'com.cloudbees.jenkins.plugins.sshcredentials.'
            'impl.BasicSSHUserPrivateKey'
        )

        if self.key_type == 0:
            c_class = base_class + '$DirectEntryPrivateKeySource'
        elif self.key_type == 1:
            c_class = base_class + '$FileOnMasterPrivateKeySource'
        elif self.key_type == 2:
            c_class = base_class + '$UsersPrivateKeySource'
        else:
            c_class = None

        attrs = {
            'value': self.key_type,
            'privateKey': self.key_value,
            'stapler-class': c_class
        }
        c_id = '' if self.credential_id is None else self.credential_id

        return {
            'stapler-class': c_class,
            'Submit': 'OK',
            'json': {
                '': '1',
                'credentials': {
                    'scope': 'GLOBAL',
                    'id': c_id,
                    'username': self.username,
                    'description': self.description,
                    'privateKeySource': attrs,
                    'passphrase': self.passphrase,
                    'stapler-class': base_class,
                    '$class': base_class
                }
            }
        }
