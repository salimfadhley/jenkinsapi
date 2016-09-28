"""
Module for Python 2 and Python 3 compatibility
"""
import six


def needs_encoding(data):
    """
    Check whether data is Python 2 unicode variable and needs to be
    encoded
    """
    if six.PY2 and isinstance(data, unicode):
        return True
    return False


def to_string(data, encoding='utf-8'):
    """
    Return string representation for the data. In case of Python 2 and unicode
    do additional encoding before
    """
    encoded_text = data.encode(encoding) if needs_encoding(data) else data
    return str(encoded_text)
