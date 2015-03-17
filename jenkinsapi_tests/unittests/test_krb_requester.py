# To run unittests on python 2.6 please use unittest2 library
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from jenkinsapi.utils.krb_requester import KrbRequester


class TestKrbRequester(unittest.TestCase):

    def test_init_ssl_verify(self):
        """
        Is the ssl_verify value passed in parent class correctly?
        """
        req = KrbRequester(True, 'http://dummy')
        self.assertTrue(req.ssl_verify == True)

        req = KrbRequester(False, 'http://dummy')
        self.assertTrue(req.ssl_verify == False)

if __name__ == "__main__":
    unittest.main()
