# -*- coding: utf-8 -*-
import six
from jenkinsapi_utils.compat import (
    to_string,
    needs_encoding,
)


def test_needs_encoding_py2():
    if six.PY2:
        unicode_str = u'юникод'
        assert needs_encoding(unicode_str)

    assert not needs_encoding('string')
    assert not needs_encoding(5)
    assert not needs_encoding(['list', 'of', 'strings'])


def test_to_string():
    assert isinstance(to_string(5), str)
    assert isinstance(to_string('string'), str)
    assert isinstance(to_string(['list', 'of', 'strings']), str)
    assert isinstance(to_string(u'unicode'), str)
