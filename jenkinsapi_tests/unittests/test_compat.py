# -*- coding: utf-8 -*-
import six
# To run unittests on python 2.6 please use unittest2 library
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from jenkinsapi_utils.compat import (
    to_string,
    needs_encoding,
)


class TestCompatUtils(unittest.TestCase):

    def test_needs_encoding_py2(self):
        if six.PY2:
            unicode_str = u'юникод'
            self.assertTrue(needs_encoding(unicode_str))

        self.assertFalse(needs_encoding('string'))
        self.assertFalse(needs_encoding(5))
        self.assertFalse(needs_encoding(['list', 'of', 'strings']))

    def test_to_string(self):
        self.assertIsInstance(to_string(5), str)
        self.assertIsInstance(to_string('string'), str)
        self.assertIsInstance(to_string(['list', 'of', 'strings']), str)
        self.assertIsInstance(to_string(u'unicode'), str)
