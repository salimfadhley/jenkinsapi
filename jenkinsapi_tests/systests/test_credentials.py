'''
System tests for `jenkinsapi.jenkins` module.
'''
import logging
# To run unittests on python 2.6 please use unittest2 library
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from jenkinsapi_tests.systests.base import BaseSystemTest
from jenkinsapi_tests.test_utils.random_strings import random_string
from jenkinsapi.credentials import Credentials
from jenkinsapi.credentials import UsernamePasswordCredential
from jenkinsapi.credentials import SecretTextCredential
from jenkinsapi.credential import SSHKeyCredential
from jenkinsapi.custom_exceptions import JenkinsAPIException

log = logging.getLogger(__name__)


class TestCredentials(BaseSystemTest):
    def test_get_credentials(self):
        creds = self.jenkins.credentials
        self.assertIsInstance(creds, Credentials)

    def test_delete_inexistant_credential(self):
        with self.assertRaises(KeyError):
            creds = self.jenkins.credentials

            del creds[random_string()]

    def test_create_user_pass_credential(self):
        creds = self.jenkins.credentials

        cred_descr = random_string()
        cred_dict = {
            'description': cred_descr,
            'userName': 'userName',
            'password': 'password'
        }
        creds[cred_descr] = UsernamePasswordCredential(cred_dict)

        self.assertTrue(cred_descr in creds)
        cred = creds[cred_descr]
        self.assertIsInstance(cred, UsernamePasswordCredential)
        self.assertEquals(cred.password, None)
        self.assertEquals(cred.description, cred_descr)

        del creds[cred_descr]

    def test_update_user_pass_credential(self):
        creds = self.jenkins.credentials

        cred_descr = random_string()
        cred_dict = {
            'description': cred_descr,
            'userName': 'userName',
            'password': 'password'
        }
        creds[cred_descr] = UsernamePasswordCredential(cred_dict)

        cred = creds[cred_descr]
        cred.userName = 'anotheruser'
        cred.password = 'password'

        with self.assertRaises(JenkinsAPIException):
            creds[cred_descr] = cred

    def test_create_ssh_credential(self):
        creds = self.jenkins.credentials

        cred_descr = random_string()
        cred_dict = {
            'description': cred_descr,
            'userName': 'userName',
            'passphrase': '',
            'private_key': '-----BEGIN RSA PRIVATE KEY-----'
        }
        creds[cred_descr] = SSHKeyCredential(cred_dict)

        self.assertTrue(cred_descr in creds)
        cred = creds[cred_descr]
        self.assertIsInstance(cred, SSHKeyCredential)
        self.assertEquals(cred.description, cred_descr)

        del creds[cred_descr]

        cred_dict = {
            'description': cred_descr,
            'userName': 'userName',
            'passphrase': '',
            'private_key': '/tmp/key'
        }
        creds[cred_descr] = SSHKeyCredential(cred_dict)

        self.assertTrue(cred_descr in creds)
        cred = creds[cred_descr]
        self.assertIsInstance(cred, SSHKeyCredential)
        self.assertEquals(cred.description, cred_descr)

        del creds[cred_descr]

        cred_dict = {
            'description': cred_descr,
            'userName': 'userName',
            'passphrase': '',
            'private_key': '~/.ssh/key'
        }
        creds[cred_descr] = SSHKeyCredential(cred_dict)

        self.assertTrue(cred_descr in creds)
        cred = creds[cred_descr]
        self.assertIsInstance(cred, SSHKeyCredential)
        self.assertEquals(cred.description, cred_descr)

        del creds[cred_descr]

        cred_dict = {
            'description': cred_descr,
            'userName': 'userName',
            'passphrase': '',
            'private_key': 'invalid'
        }
        with self.assertRaises(ValueError):
            creds[cred_descr] = SSHKeyCredential(cred_dict)

    def test_create_secret_text_credential(self):
        """
        Tests the creation of a secret text.
        """
        creds = self.jenkins.credentials

        cred_descr = random_string()
        cred_dict = {
            'description': cred_descr,
            'secret': 'newsecret'
        }
        creds[cred_descr] = SecretTextCredential(cred_dict)

        self.assertTrue(cred_descr in creds)
        cred = creds[cred_descr]
        self.assertIsInstance(cred, SecretTextCredential)
        self.assertEquals(cred.secret, None)
        self.assertEquals(cred.description, cred_descr)

        del creds[cred_descr]

    def test_delete_credential(self):
        creds = self.jenkins.credentials

        cred_descr = random_string()
        cred_dict = {
            'description': cred_descr,
            'userName': 'userName',
            'password': 'password'
        }
        creds[cred_descr] = UsernamePasswordCredential(cred_dict)

        del creds[cred_descr]


if __name__ == '__main__':
    logging.basicConfig()
    unittest.main()
